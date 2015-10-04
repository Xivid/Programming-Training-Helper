from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, RequestContext
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from models import problem, realauth

def index(request):
	if request.user.is_authenticated():
		canpublish = False
		if Group.objects.get(name = "Publisher") in request.user.groups.all():
			canpublish = True
		c = Context({"navusername": request.user.username, "navuserid": request.user.id, "canpublish": canpublish, "totalproblemnumber": len(problem.objects.all()), "annoynumber": len(list(problem.objects.filter(hint = '')))})
		return render_to_response("index.html", c)
	else:
		return render_to_response("default.html")

def login(request):
	if request.POST:
		user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
		if user is not None and user.is_active:
			auth.login(request, user)
			return HttpResponseRedirect("/")
		else:
			return render_to_response("default.html", Context({"loginerr": True}))
	else:	
		return HttpResponseRedirect("/")

def reg(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect("/")
	else:
		if request.POST:
			name = request.POST["username"]
			
			pass1 = request.POST["password"]
			pass2 = request.POST["repassword"]
			
			empty = False
			namevalid = True
			passvalid = True
			if name=="" or pass1=="" or pass2=="":
				empty = True
			u = User.objects.filter(username=name)
			if len(u)>0:
				namevalid = False
			if pass1 != pass2:
				passvalid = False
			if (not empty) and namevalid and passvalid:
				user = User.objects.create_user(username = name, password = pass1)
				user.is_staff = False
				user.groups.add(Group.objects.get(name = "User"))
				user.save()
				user = auth.authenticate(username=name, password=pass1)
				#myuser.groups = [group_list]
				auth.login(request, user)
				return HttpResponseRedirect("/")
			return render_to_response("default.html",{'invalidname': not namevalid, 'invalidpass': not passvalid, 'empty': empty, })
		else:
			return HttpResponseRedirect("/")

@login_required
def showuserinfo(request):
	if request.GET:
		canpublish = False
		if Group.objects.get(name = "Publisher") in request.user.groups.all():
			canpublish = True
		if request.user.id == int(request.GET["id"]):
			isself=True
			if request.user.username == "publish":
				isself = False
			notsame=False
			oldwrong=False
			success=False
			if request.POST:
				old = request.POST["old"]
				new1 = request.POST["password"]
				new2 = request.POST["repassword"]
				if request.user.check_password(old):
					if new1==new2:
						request.user.set_password(new1)
						request.user.save()
						success=True
					else:
						notsame = True
				else:
					oldwrong = True

			if len(realauth.objects.filter(user = request.user)) > 0:
				authuser = realauth.objects.get(user = request.user)
				authid = authuser.identity
				authname = authuser.name
				is_active = authuser.is_active
				info = Context({'isself': isself, 'userid': request.user.id, 'navusername': request.user.username, 'canpublish': canpublish,
								'notsame': notsame, 'oldwrong': oldwrong, 'success': success,"username": request.user.username, "isrealauthed": True, "authname": authname, "authid": authid, "is_active": is_active,})
			else:
				info = Context({'isself': isself, 'userid': request.user.id, 'navusername': request.user.username, 'canpublish': canpublish,
								'notsame': notsame, 'oldwrong': oldwrong, 'success': success,"username": request.user.username, "isrealauthed": False, })
			return render_to_response("userinfo.html", info)
		else:
			ID = int(request.GET["id"])
			username = User.objects.get(id=ID).username
			isrealauthed = False
			if len(realauth.objects.filter(user = User.objects.get(id=ID)))>0:
				isrealauthed = True
				authname = realauth.objects.get(user = User.objects.get(id=ID)).name
				authid = realauth.objects.get(user = User.objects.get(id=ID)).identity
				is_active = realauth.objects.get(user = User.objects.get(id=ID)).is_active
				info = Context({'isrealauthed': isrealauthed, 'navusername': request.user.username, 'userid': request.user.id,
								'username': username, "authname":authname, "is_active":is_active,"authid":authid, 'canpublish': canpublish,})
			else:
				info = Context({'isrealauthed': isrealauthed, 'navusername': request.user.username, 'userid': request.user.id,
								'username': username, 'canpublish': canpublish,})
			return render_to_response("userinfo.html", info)
	return HttpResponseRedirect("/")


def help(request):
	canpublish = False
	if Group.objects.get(name = "Publisher") in request.user.groups.all():
		canpublish = True
	return render_to_response("help.html", Context({'navusername': request.user.username, 'navuserid': request.user.id, 'canpublish': canpublish,}));

@login_required
def postentry(request):
	if Group.objects.get(name = "Publisher") in request.user.groups.all():
		if request.GET and not request.POST:
			c = Context({"hasname": request.GET["qname"], 'canpublish': True, 
				'navusername': request.user.username, 'navuserid': request.user.id, })
			return render_to_response("post.html", c)
		if request.POST:
			if len(problem.objects.filter(name = request.POST["qname"])) > 0:
				return HttpResponse("has existed!")
			if request.POST["qname"]=="":
				return HttpResponse("Please input the problem name!!!")
			new_problem = problem(
				creator = request.user,
				editor = str(request.user.id),
				name = request.POST["qname"].upper(),
				description = request.POST["qdesc"],
				hint = request.POST["qhint"],
				inputformat = request.POST["qiformat"],
				outputformat = request.POST["qoformat"],
				inputsample = request.POST["qinsample"],
				outputsample = request.POST["qoutsample"],
				solution = request.POST["qsolution"],
				code = request.POST["qcode"],
				mycode = request.POST["qmycode"],
				viewcount = 0)

			new_problem.save()
			c = Context({"published": True, 'canpublish': True, 
				"qname": request.POST["qname"],'navusername': request.user.username, 'navuserid': request.user.id,})
			return render_to_response("post.html", c)
		
		return render_to_response("post.html", Context({'navusername': request.user.username, 'canpublish': True, 'navuserid': request.user.id,}))
	else:
		return HttpResponseRedirect("/")

@login_required
def showentry(request):
	if request.GET:
		canpublish = False
		if Group.objects.get(name = "Publisher") in request.user.groups.all():
			canpublish = True
		if len(problem.objects.filter(name = request.GET["qname"].upper())) > 0:
			q = problem.objects.get(name = request.GET["qname"])
			q.viewcount += 1
			q.save()
			c = Context({"creatorurl": "/accounts/userinfo/?id="+str(q.creator.id), 
					#"creator": realauth.objects.get(user=q.creator).name, 
					"creator": q.creator.username, 
					"editor": q.editor + "(this element to be improved by a dict)",
					"qname": q.name,
					"qdesc": q.description,
					"qhint": q.hint,
					"qiformat": q.inputformat,
					"qoformat": q.outputformat,
					"qinsample": q.inputsample,
					"qoutsample": q.outputsample,
					"qsolution": q.solution,
					"qcode": q.code,
					"qmycode": q.mycode,
					"canpublish": canpublish,
					"qid": q.id,
					"viewcount": q.viewcount,
					"isadmin": True if Group.objects.get(name = "Administrator") in request.user.groups.all() else False,
					'navusername': request.user.username, 'navuserid': request.user.id,
				})
		else:
			c = Context({"notfound": True, "qname": request.GET["qname"],"canpublish": canpublish,'navusername': request.user.username, 'navuserid': request.user.id, })
		return render_to_response("show.html", c);

@login_required
def editentry(request):
	if request.GET:
		if Group.objects.get(name = "Publisher") in request.user.groups.all():
			if request.POST:
				p = request.POST
				q = problem.objects.get(id = request.GET["id"])
				q.description = p["qdesc"]
				q.hint = p["qhint"]
				q.inputformat = p["qiformat"]
				q.outputformat = p["qoformat"]
				q.inputsample = p["qinsample"]
				q.outputsample = p["qoutsample"]
				q.solution = p["qsolution"]
				q.code = p["qcode"]
				q.mycode = p["qmycode"]
				q.save()
				c = Context({
					"published": True,
					"qname": q.name,
					"qdesc": q.description,
					"qhint": q.hint,
					"qiformat": q.inputformat,
					"qoformat": q.outputformat,
					"qinsample": q.inputsample,
					"qoutsample": q.outputsample,
					"qsolution": q.solution,
					"qcode": q.code,
					"canpublish": True,
					"qmycode": q.mycode,
					'navusername': request.user.username, 'navuserid': request.user.id,
					})
			else:
				q = problem.objects.get(id = request.GET["id"])
				c = Context({
						"qname": q.name,
						"qdesc": q.description,
						"qhint": q.hint,
						"qiformat": q.inputformat,
						"qoformat": q.outputformat,
						"qinsample": q.inputsample,
						"qoutsample": q.outputsample,
						"qsolution": q.solution,
						"canpublish": True,
						"qcode": q.code,
						"qmycode": q.mycode,
						'navusername': request.user.username, 'navuserid': request.user.id,
					})
			return render_to_response("edit.html", c)

@login_required
def delentry(request):
	if Group.objects.get(name = "Administrator") in request.user.groups.all():
		if request.GET:
			if request.POST:
				if request.POST["confirm"]=="yes":
					problem.objects.get(id=request.GET["id"]).delete()
					return render_to_response("delete.html", Context({"success": True,"canpublish": True,}))
				else:
					return HttpResponseRedirect("/")
			else:
				return render_to_response("delete.html", Context({'navusername': request.user.username,"canpublish": True, 'navuserid': request.user.id,}))

@login_required
def allentry(request):
	canpublish = False
	if Group.objects.get(name = "Publisher") in request.user.groups.all():
		canpublish = True
	problem_list = list(problem.objects.all())
	problem_list.sort(key = lambda x: int(x.name[1:]), reverse = False)
	c = Context({"problem_list": problem_list, 'canpublish': canpublish, 'navusername': request.user.username, 'navuserid': request.user.id,})
	return render_to_response("all.html", c)

@login_required
def annoyentry(request):
	canpublish = False
	if Group.objects.get(name = "Publisher") in request.user.groups.all():
		canpublish = True
	problem_list = list(problem.objects.filter(hint = ' '))
	problem_list.sort(key = lambda x: int(x.name[1:]), reverse = False)
	c = Context({"problem_list": problem_list, 'canpublish': canpublish, 'navusername': request.user.username, 'navuserid': request.user.id,})
	return render_to_response("annoy.html", c)

@login_required
def processrealauth(request):
	if request.GET:
		if request.GET["action"] == 'apply':
			if len(realauth.objects.filter(user_id = request.user.id)) == 0:
				newuser = realauth(
					user = request.user,
					identity = request.GET["number"],
					name = request.GET['realname'],
					is_active = False,
				)
				newuser.save()

				return HttpResponseRedirect("/accounts/userinfo/?id="+str(request.user.id))
			else:
				return HttpResponse("You've applied real-authenticating.")
		elif request.GET["action"] == 'accept':
			if Group.objects.get(name = "Administrator") in request.user.groups.all():
				realuser = realauth.objects.get(id = request.GET["id"])
				realuser.is_active = True
				realuser.save()
				user = User.objects.get(id = realuser.user.id)
				user.groups.add(Group.objects.get(name = "publisher"))
				user.save()
				return HttpResponseRedirect("/accounts/realauth/")
			else:
				return HttpResponse("Permission Denied.")
		elif request.GET["action"] == 'decline':
			if Group.objects.get(name = "Administrator") in request.user.groups.all():
				realuser = realauth.objects.get(id = request.GET["id"])
				user = User.objects.get(id = realuser.user.id)
				user.groups.remove(Group.objects.get(name = "publisher"))
				user.save()
				realuser.delete()

				return HttpResponseRedirect("/accounts/realauth/")
			else:
				return HttpResponse("Permission Denied.")
		else:
			return HttpResponse("Invalid command.")
	else:
		if Group.objects.get(name = "Administrator") in request.user.groups.all():
			userlist = list(realauth.objects.all())
			return render_to_response("realmanage.html", Context({"userlist": userlist, "canpublish": True, "navuserid": request.user.id, "navusername": request.user.username}))
		elif Group.objects.get(name = "Publisher") in request.user.groups.all():
			return HttpResponseRedirect("/accounts/userinfo/?id=" + str(request.user.id))
		else:
			return HttpResponseRedirect("/")