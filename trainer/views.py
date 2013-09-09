# -*- coding: utf-8 -*- 
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from django.shortcuts import render_to_response
from django.template import RequestContext
import datetime, re, sys, time
from functools import wraps
from TZM.trainer.models import *
import models
from django.contrib.auth import models, authenticate, login, logout
from BeautifulSoup import BeautifulSoup, Tag, NavigableString
from defimg import DEFAULT_USER_IMG
import json
from django.template.defaultfilters import stringfilter
import subprocess

blender_path = '/home/dan/TZM/wxui/run.sh'

def render_to(tmpl, mimetype=None):
    """
    Декоратор, отправляющий результат работы функции в указанный шаблон tmpl.
    tmpl - имя шаблона
    mimetype - mime-type шаблона
    """
    def renderer(func):
        @wraps(func)
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if isinstance(output, (list, tuple)):
                return render_to_response(output[1], output[0], RequestContext(request), mimetype=mimetype)
            elif isinstance(output, dict):
                return render_to_response(tmpl, output, RequestContext(request), mimetype=mimetype)
            return output
        return wrapper
    return renderer

def need_auth(func):
    """
    Декоратор, проверяет аутентификацию пользователя.
    Используется только для view, которые возвращают HttpResponse
    func - функция над которой применен декоратор
    """	
    @wraps(func)
    def wrapper(request, *args, **kw):
        if request.user.is_authenticated():
            output = func(request, *args, **kw)
            return output
        else:
            return HttpResponse('', status=401)
    return wrapper

def need_auth_html(func):
    """
    Декоратор, проверяет аутентификацию пользователя.
    Используется только для view, которые возвращают HttpResponse
    func - функция над которой применен декоратор
    """
    @wraps(func)
    def wrapper(request, *args, **kw):
        if request.user.is_authenticated():
            output = func(request, *args, **kw)
            return output
        else:
            return HttpResponseRedirect('/trainer/login')
    return wrapper

def render_need_auth(func):
    """
    Декоратор, проверяет аутентификацию пользователя.
    Используется только после декоратора render_to
    func - функция над которой применен декоратор
    """
    @wraps(func)
    def wrapper(request, *args, **kw):
        if request.user.is_authenticated():
            output = func(request, *args, **kw)
            return output
        else:
            return {}, '401.xml'
    return wrapper

def getphoto(request, username):
    try:
        photo = Photo.objects.get(user = auth_models.User.objects.get(username = username))
        photo.img.open()
        content = photo.img.read()
        photo.img.close()
        print 'userimg'
        return HttpResponse(content)
    except (IOError, ValueError, ObjectDoesNotExist):
        print 'defimg'
        return HttpResponse(DEFAULT_USER_IMG, mimetype='image/png')

def newuser(request, persname):
        raise NotImplementedError()
        p = Person(name = persname)
        p.save()
        return HttpResponse('ok')

def userlist(request):
        x = BeautifulSoup()
        root = Tag(x,'root')
        x.insert(0,root)
        for u in models.Group.objects.get(name='Курсанты').user_set.all():
                root.insert(0,'\n')
                root.insert(0,Tag(x,'user',[
                        ('uid',str(u.id)),
                        ('username',u.username),
                        ('first_name',u.first_name),
                        ('last_name',u.last_name),
                        ]))
        
        return HttpResponse(x)

@render_to('statelist.xml', mimetype='text/xml')
@render_need_auth
def statelist(request):
    """
    По текущему пользователю возвращаем последние его результаты, привязанные к модулям, темам и дидактическим единицам
    request - стандартный объект HttpRequest фреймворка Django
    """
    logs = {}
    #в logs добавляем только самые поздние по дате RELog
    for log in RELog.objects.filter(user=request.user).order_by('-date'):
        if not log.category_id in logs:
            logs[log.category_id] = {}
        if not log.type_log in logs[log.category_id]:
            logs[log.category_id][log.type_log] = log
    categories = RECategory.objects.filter(parent__isnull=True).order_by('number')
    return {'categories': categories, 'user': request.user, 'logs': logs}

@render_to('testslist.xml', mimetype='text/xml')
@render_need_auth
def testslist(request):
    """
    Возвращает список всех тестов
    request - стандартный объект HttpRequest фреймворка Django
    """
    tests = RETestQuestion.objects.all()
    return {'tests': tests}

@render_to('test.xml', mimetype='text/xml')
@render_need_auth
def test_by_id(request, category_id, question_count=None):
    """
    Возвращает случайный список вопросов
    request - стандартный объект HttpRequest фреймворка Django
    category_id - идентификатор модуля, темы или дидактической единицы
    question_count - необходимое количество вопросов
    """
    if question_count is None:
        question_count = 1
    else:
        question_count = int(question_count)
    try:
        category = RECategory.objects.get(pk=category_id)
    except ObjectDoesNotExist: 
        category = None
        questions = None
    else:
        category_ids = category.get_ids()
        questions = RETestQuestion.objects.filter(category__id__in=category_ids).order_by('?')
        if 'questions_id' in request.session:
            _questions = questions.exclude(id__in=request.session['questions_id'])
            if _questions.count() >= question_count:
                questions = _questions

        questions = questions[:question_count]
        questions_id = [question.id for question in questions]
        if 'questions_id' in request.session:
            request.session['questions_id'].update(questions_id)
            request.session.modified = True
        else:
            request.session['questions_id'] = set(questions_id)

    return {'category': category, 'questions': questions}
    
def test_by_id_for_html(request, category_id, question_count=None):
    """
    Возвращает случайный список вопросов
    request - стандартный объект HttpRequest фреймворка Django
    category_id - идентификатор модуля, темы или дидактической единицы
    question_count - необходимое количество вопросов
    """
    if question_count is None:
        question_count = 1
    else:
        question_count = int(question_count)
    try:
        category = RECategory.objects.get(pk=category_id)
    except ObjectDoesNotExist: 
        category = None
        questions = None
    else:
        category_ids = category.get_ids()
        questions = RETestQuestion.objects.filter(category__id__in=category_ids).order_by('?')
        if 'questions_id' in request.session:
            _questions = questions.exclude(id__in=request.session['questions_id'])
            if _questions.count() >= question_count:
                questions = _questions

        questions = questions[:question_count]
        questions_id = [question.id for question in questions]
        if 'questions_id' in request.session:
            request.session['questions_id'].update(questions_id)
            request.session.modified = True
        else:
            request.session['questions_id'] = set(questions_id)

    return questions

@render_to('auth.xml', mimetype='text/xml')
def tzm_login(request):
    """
    Аутентификация пользователя
    request - стандартный объект HttpRequest фреймворка Django
    http-методом GET или POST передаются переменные:
    username - имя пользователя
    password - пароль пользователя
    POST имеет преимущество перед GET
    """
    #if request.user.is_authenticated():
    #    logout(request)
    username = request.POST.get('username') or request.GET.get('username')
    password = request.POST.get('password') or request.GET.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return {'user': user, 'session_key': request.session.session_key}
        else:
            return {'error': u'Пользователь заблокирован'}
    else:
        return {'error': u'Ошибка в имени или пароле'}

@need_auth
def tzm_logout(request):
    """
    Деаутентификация пользователя
    request - стандартный объект HttpRequest фреймворка Django
    """
    logout(request)
    return HttpResponse('')

@need_auth
def log(request, category_id, type_log, rating):
    """
    Запись действий пользователя в лог
    request - стандартный объект HttpRequest фреймворка Django
    category_id - идентификатор модуля, темы или дидактической единицы
    type_log - тип действия, соответствует словарю TYPE_LOG_CHOICES
    rating - оценка дейсвия
    так же http-методом GET или POST передаются необязательные переменные:
    seconds - время затраченное на действие, в секундах
    context - индетификатор контекста
    description - текстовое описание
    POST имеет преимущество перед GET
    """
    try:
        category = RECategory.objects.get(pk=category_id)
    except ObjectDoesNotExist:
        return HttpResponse('oops', status=404)
    seconds = request.POST.get('seconds') or request.GET.get('seconds')
    context = request.POST.get('context') or request.GET.get('context')
    description = request.POST.get('description') or request.GET.get('description')
    RELog.objects.create(
        category=category,
        user=request.user,
        type_log=type_log,
        rating=rating,
        seconds=seconds,
        context=context,
        description=description)
    return HttpResponse('')

'''
@need_auth
def start_sync(request, category_id, type_log):
    """
    Создание нового блока синхронизации
    request - стандартный объект HttpRequest фреймворка Django
    category_id - идентификатор модуля, темы или дидактической единицы
    type_log - тип действия, соответствует словарю TYPE_LOG_CHOICES
    """
    try:
        category = RECategory.objects.get(pk=category_id)
    except ObjectDoesNotExist:
        return HttpResponse('oops', status=404)
    block = RESyncBlock.objects.create(
        category=category,
        type_log=type_log)
    return HttpResponse(block.id)

@need_auth
def end_sync(request, block_id):
    """
    Завершение блока синхронизации
    request - стандартный объект HttpRequest фреймворка Django
    block_id - идентификатор блока синхронизации
    """
    try:
        block = RESyncBlock.objects.get(pk=block_id)
        block.date_end = datetime.datetime.now()
        block.save()
    except ObjectDoesNotExist:
        return HttpResponse('oops', status=404)
    return HttpResponse('')

@need_auth
def sync_log(request, block_id):
    """
    Создание нового блока синхронизации (использование http-метода POST) 
    или получение лога синхронизации (использование http-метода GET) 
    request - стандартный объект HttpRequest фреймворка Django
    block_id - идентификатор блока синхронизации
    при создании, http-методом POST передается переменная:
    key - код уравляещего элемента
    при получении, http-методом GET передается необязательные переменная:
    id - индетификатор последнего действия, после которого нужно получить лог,
    при его отсутсвии возвращаются последние 5 действий
    """
    try:
        block = RESyncBlock.objects.get(pk=block_id)
    except ObjectDoesNotExist:
        return HttpResponse('oops', status=404)
    if request.method == 'POST':
        if block.date_end:
            #обсудить что возвращать
            return HttpResponse('oops', status=404)
        log = RESyncLog.objects.create(
            block=block,
            key=request.POST.get('key'))
        return HttpResponse(log.id)
    else:
        logs = RESyncLog.objects.filter(block=block).order_by('-id')
        #нужна ли такая проверка
        """
        if block.date_end:
            return HttpResponse('oops', status=404)
        """
        last_id = request.GET.get('id')
        if last_id:
            logs = logs.filter(id__gt=last_id)
        else:
            logs = logs[:5]
        buff = ''
        for log in logs:
            buff += '%s:%s:%s\n' % (log.id, log.key, (log.date - block.date).total_seconds())
        return HttpResponse(buff)
'''

@need_auth
def sync_state(request):
    """
    Изменение состояние синхронизации (при наличии в запросе переменной state)
    или получение состояние синхронизации (при отсутсвии в запросе переменной state) 
    request - стандартный объект HttpRequest фреймворка Django
    для изменения состояния: state = 0 - синхронизация выключается, в остальных случаях включается
    """
    sync_state = RESyncState.get_state()
    is_sync = request.POST.get('state') or request.GET.get('state') or None
    if not is_sync is None:
        sync_state.is_sync = is_sync != '0'
        sync_state.save()
    return HttpResponse('<state>%s</state>' % sync_state.is_sync)


@need_auth
def sync(request):
    """
    Запись в лог синхронизации (использование http-метода POST или наличие key в GET) 
    или получение лога синхронизации (использование http-метода GET) 
    request - стандартный объект HttpRequest фреймворка Django
    при создании, http-методом POST передается переменная:
    key - код уравляещего элемента
    при получении, http-методом GET передается необязательные переменная:
    id - индетификатор последнего действия, после которого нужно получить лог,
    при его отсутсвии возвращаются последние 50 действий
    На результат влияет значения поля is_sync в модели RESyncState
    """
    context = request.GET.get('context')
    if request.GET.get('key') is None:
        logs = RESync.objects.all().order_by('-id')
        if context:
            logs = logs.filter(context=context)

        sync_state = RESyncState.get_state()
        if not sync_state.is_sync:
            logs = logs.filter(user=request.user)

        last_id = request.GET.get('id')
        if last_id:
            logs = logs.filter(id__gt=last_id)
        else:
            logs = logs[:50]
        buff = ''
        for log in logs:
            buff += '%s:%s:%s:%s\n' % (log.id, log.key, long(time.mktime(log.date.timetuple())), log.context if log.context else '')
        return HttpResponse(buff)
    else:
        log = RESync.objects.create(
            user=request.user,
            key=request.GET.get('key'),
            context=context)
        return HttpResponse(log.id)

@render_to('sync_admin.html')
def sync_admin(request):
    sync_state = RESyncState.get_state()
    return {'sync_state': sync_state.is_sync}

'''@register.filter(name='myfilter')
def myfilter(dict,key):
	try:
		dict[key]
	except (ValueError, ZeroDivisionError):
		return ""
'''
def login_html(request):
	errors = []
	password = ''
	selectedUser = ''
	print blender_path
	'''for photo in Photo.objects.all():
		photos[photo.user.username] = photo.img.url'''
	if request.method == 'POST':
		print 'post'
		if not request.POST.get('Password', ''):
			errors.append(u'Введите пароль')	
		if not request.POST.get('userlist', ''):
			errors.append(u'Выберите пользователя')
		selectedUser = request.POST.get('userlist')
		password = request.POST.get('Password')
		if selectedUser != '' and password != '' :
			user = authenticate(username=selectedUser, password=password)
			print password
			print selectedUser
			if user is not None:
				print 'exist!!'
				if user.is_active:
					print 'active!'
					request.session['user'] = user
					login(request, user)
					return HttpResponseRedirect('/trainer/UserPage') 
				else:
				    errors.append(u'Пользователь заблокирован')
			else:
			    errors.append(u'Ошибка в имени или пароле')
	return render_to_response('Login.html', {'Password': password, 'collection' : models.Group.objects.get(name='Курсанты').user_set.all(), 'errors': errors, 'selectedUser': selectedUser})

@need_auth_html
def userPage_html(request):
	user = request.user
	#request.session['categories'] = AllCategories(request)
	#categories = request.session['categories'] 
	categories = AllCategories(request)
	#logs = {}
	selectedCategory = None;
	#sl = statelist(request);
	print 'models:'
	#for log in RELog.objects.filter(user=user.id).order_by('-date'):
	#		if not log.category_id in logs:
	#			logs[log.category_id] = {}
	#			print log.get_model_fields
	#		if not log.type_log in logs[log.category_id]:
	#			logs[log.category_id][log.type_log] = log
	#print logs
	if request.method == 'POST':
		print 'post'
		catId = request.POST.get('variable')
		actionType = request.POST.get('actionType')
		if actionType == 'test':
			print catId
			request.session['categoryId'] = catId
			testCount = 10
			request.session['questsCount'] = testCount
			request.session['rightAnswers'] = 0
			request.session['tests'] = test_by_id_for_html(request, catId, testCount)
			request.session['questNumber'] = 0
			print 'categoryId' + request.session['categoryId']
			return HttpResponseRedirect('/trainer/Test')
		elif actionType == 'logout':
			tzm_logout(request)
			return HttpResponseRedirect('/trainer/login')
		elif actionType == 'practice':
			print 'openBlender'
			subprocess.Popen(['blender', '/home/dan/project.blend'])
			photo = Photo.objects.get(user = user)
	else:
		print 'get'
		#for log in RELog.objects.filter(user=user.id).order_by('-date'):
			#if not log.category_id in logs:
			#	logs[log.category_id] = {}
			#if not log.type_log in logs[log.category_id]:
			#	logs[log.category_id][log.type_log] = log
		photo = Photo.objects.get(user = user)
		#photo.img.open()
        #content = photo.img.read()
        #photo.img.close()
		#photo = getphoto(request, user.username)
		#content = (DEFAULT_USER_IMG, mimetype='image/png')
		# RECategory.objects.filter(parent__isnull=True).order_by('number')
		#coljson = [category.json() for category in categories]
		#for category in categories:
			#print category
			#childcats = category.children()
			#for cat in childcats:
				#print cat
		#categoriesjson = json.dumps(coljson)
		#jsoncat = json.dumps({ "status": "success", "message": "everything's fine" })
		#return {'categories': categories, 'user': request.user, 'logs': logs}
		#print 'user '
		print 'photo:'
		print photo
		print photo.img.url
		print photo.img.path
		
	request.session['val1'] = 0
	val1 = 0
	return render_to_response('UserPage.html', {'user': user, 'categories': categories, 'val1': val1
	, 'photo': photo
	})

def AllCategories(request):
	print 'allcat'
	x = BeautifulSoup()
	#root = Tag(x,'ul', [('class', "tree"), ( 'id', "tree")])
	#x.insert(0,root)
	AllCategories = RECategory.objects.filter(parent__isnull=True).order_by('-number')
	
	AllAnswered = {}
    #в logs добавляем только самые поздние по дате RELog
	for log in RELog.objects.filter(user=request.user).order_by('-date'):
		if not log.category_id in AllAnswered:
			AllAnswered[log.category_id] = {}
		if not log.type_log in AllAnswered[log.category_id]:
			AllAnswered[log.category_id][log.type_log] = log
	for category in AllCategories:
		print category.id
		nt = Tag(x,'li', [("id", str(category.id))])
		log = AllAnswered.get(category.id)
		rating = ''
		if log:
			log = log.get(5)
			if log :
				rating = 'Оценка: ' + str(log.rating)
		div = Tag(x,'div')
		div.string = rating
		div["class"] = "rating"
		#div["style"] = "width: 150px; float: right;"
		nt.insert(0, div)
		
		if category.is_3d:
			isDDD = "Есть";
		else:
			isDDD = "Нет";
		div = Tag(x,'div')
		div.string = isDDD 
		div["class"] = "is3d"
		#div["style"] = "margin-right: 0px;width: 110px; float: right;"
		nt.insert(0, div)
		
		div = Tag(x,'div')
		div["class"] = "demo"
		#div["style"] = "margin-right: 0px;width: 110px; float: right;"
		div.string = str(category.type_category)
		nt.insert(0, div)
		
		div = Tag(x,'div')
		div.string = category.name
		nt.insert(0, div)
		
		x.insert(0,nt)
		recurseCategories(category, nt, x, AllAnswered)
	res = x.prettify()
	#print res
	print 'endallcat'
	return res

def recurseCategories(parentCat, root, x, AllAnswered):
	childcats = parentCat.children()
	if childcats:
		nt = Tag(x,'ul', [('style', 'display:none')])
		root.insert(len(root.contents),nt)
		root = nt
	for category in childcats:
		root.insert(len(root.contents),'\n')
		nt = Tag(x,"li", [("id", str(category.id))])		
		log = AllAnswered.get(category.id)
		rating = ''
		if log:
			log = log.get(5)
			if log :
				rating = 'Оценка: ' + str(log.rating)
		div = Tag(x,'div')
		div.string = rating
		div["class"] = "rating"
		#div["style"] = "width: 150px; float: right;"
		nt.insert(0, div)
		
		if category.is_3d:
			isDDD = "Есть";
		else:
			isDDD = "Нет";
		div = Tag(x,'div')
		div.string = isDDD 
		div["class"] = "is3d"
		#div["style"] = "margin-right: 0px;width: 110px; float: right;"
		nt.insert(0, div)
		
		div = Tag(x,'div')
		div["class"] = "demo"
		#div["style"] = "margin-right: 0px;width: 110px; float: right;"
		div.string = str(category.type_category)
		nt.insert(0, div)
		
		div = Tag(x,'div')
		div.string = category.name
		nt.insert(0, div)
		
		root.insert(len(root.contents), nt)
		
		recurseCategories(category, nt, x, AllAnswered)
#soup.body.insert(len(soup.body.contents), yourelement)

'''def test_html(request):
	categoryId = request.session['categoryId']
	tests = request.session['tests']
	print tests
	bs = BeautifulSoup(str(tests))
	actionType = ''
	questions = bs.findAll('quest')
	questCount = len(questions)
	rightAnswers = request.session['rightAnswers']
	if request.method == 'POST':
		print 'post'
		method = request.POST
		print request.POST.get('actionType')
		rightAnswer = request.POST.get('variable')
		if rightAnswer == 'true':
			rightAnswers = rightAnswers + 1
			request.session['rightAnswers'] = rightAnswers
			print rightAnswer
	else:
		print 'get'
		method = request.GET
	actionType = method.get('actionType')
	print 'actionType'
	print actionType
	if actionType == 'next':
		request.session['questNumber'] += 1
	questNumber = request.session['questNumber']
	if questNumber >= questCount:
		return HttpResponseRedirect('/trainer/Results')
	quest = questions[questNumber];
	testHtml = ConvertToTestHtml(request,quest)
	print questNumber
	return render_to_response('Test.html', {'tests': testHtml, 'questNumber': questNumber, 'questCount': questCount,
	'actionType': actionType, 'rightAnswers': rightAnswers})
'''
@need_auth_html
def test_html(request):
	categoryId = request.session['categoryId']
	actionType = ''
	questions = request.session['tests']
	questCount = len(questions)
	rightAnswers = request.session['rightAnswers']
	if request.method == 'POST':
		print 'post'
		method = request.POST
		print request.POST.get('actionType')
		rightAnswer = request.POST.get('variable')
		if rightAnswer == 'true':
			rightAnswers = rightAnswers + 1
			request.session['rightAnswers'] = rightAnswers
			print rightAnswer
	else:
		print 'get'
		method = request.GET
	actionType = method.get('actionType')
	print 'actionType'
	print actionType
	if actionType == 'next':
		request.session['questNumber'] += 1
	questNumber = request.session['questNumber']
	if questNumber >= questCount:
		return HttpResponseRedirect('/trainer/Results')
	quest = questions[questNumber];
	testHtml = ConvertToTestHtml(quest)
	print questNumber
	return render_to_response('Test.html', {'tests': testHtml, 'questNumber': questNumber, 'questCount': questCount,
	'actionType': actionType, 'rightAnswers': rightAnswers})

'''def ConvertToTestHtml(request,quest):
	value = quest.prettify()
	bs = BeautifulSoup(value)
	newbs = BeautifulSoup()
	titles = bs.findAll('txt')
	answers = bs.findAll('answer')
	pNode = Tag(newbs, 'p')
	newbs.insert(0,pNode)
	if quest.img:
		print 'Image!!!'
		quest = 
		print quest
		print quest.img.url
		print 'newtest'
		quests = test_by_id_for_html(request, 1, 3)
		print quests
		quests_ids = []
		for quest_id in quests:
			quests_ids.append(quest_id.id)
		print 'newAnswers'
		print RETestAnswer.objects.filter(question__id__in=quests_ids)
		#imageNode = Tag(newbs, 'image', [('src', quest.img.url)])
		#newbs.insert(0,imageNode)
	for title in titles:
		TitleNode = Tag(newbs, 'p')
		TitleNode.string =title.string
		newbs.insert(0,TitleNode)
	i = 0
	for answer in answers:
		radioname = 'ans' + str(i)
		nt = Tag(newbs,'input', [('type', 'radio'), ('type', radioname), ('name', 'answerradio'), ('value', answer['correct'])])
		nt.string = answer.string
		pNode.insert(len(pNode.contents), nt)
		pNode.insert(len(pNode.contents), Tag(newbs, 'br'))
	
	return newbs.prettify()
'''

def ConvertToTestHtml(quest):
	types = quest.type
	titles = quest.text
	quests_ids = [quest.id]
	answers = RETestAnswer.objects.filter(question__id__in=quests_ids)
	newbs = BeautifulSoup()
	pNode = Tag(newbs, 'p')
	newbs.insert(0,pNode)
	if quest.img:
		print 'Image!!!'
		print quest.img.url
		imageNode = Tag(newbs, 'image', [('src', quest.img.url)])
		newbs.insert(0,imageNode)
	TitleNode = Tag(newbs, 'p')
	TitleNode.string = titles
	newbs.insert(0,TitleNode)
	i = 0
	if types != 1:
		for answer in answers:
			radioname = 'ans' + str(i)
			nt = Tag(newbs,'input', [('type', 'radio'), ('type', radioname), ('name', 'answerradio'), ('value', str(answer.is_correct))])
			nt.string = answer.name
			pNode.insert(len(pNode.contents), nt)
			pNode.insert(len(pNode.contents), Tag(newbs, 'br'))
	else:
		for answer in answers:
			radioname = 'ans' + str(i)
			nt = Tag(newbs,'input', [('type', 'text'), ('name', 'answertext'),('ans', answer.name)])
			pNode.insert(len(pNode.contents), nt)
			pNode.insert(len(pNode.contents), Tag(newbs, 'br'))
	return newbs.prettify()
	
@need_auth_html
def results_html(request):
	questionCount = request.session['questsCount']
	rightAnswers = request.session['rightAnswers']
	resultInt = rightAnswers * 100.0 / questionCount ;
	result = str(rightAnswers * 100.0 / questionCount) + '%'
	if resultInt >= 85:
		evaluation = 'отлично'
		rating = 5
	elif resultInt >= 70:
		evaluation = 'хорошо'
		rating = 4
	elif resultInt >= 55:
		evaluation = 'удовлетворительно'
		rating = 3
	else:
		evaluation = 'неудовлетворительно'
		rating = 2
	categoryId = request.session['categoryId']
	log(request,categoryId,5,rating)
	return render_to_response('Results.html', {'questionCount': questionCount, 'rightAnswers': rightAnswers, 'result': result, 'evaluation': evaluation})

def show_sample_video(request, d):
	aaa = RECategory.objects.get(id=d)
	video = aaa.codevideo
	return render_to_response('video_sample.html', {'video':video})