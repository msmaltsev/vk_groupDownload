# !usr/env/bin python3
# -*- coding: utf8 -*-

import datetime, time, json, sys
import requests as req
import os

def loadListFromFile(f = 'group_ids_list.txt'):
    a = open(f, encoding='utf8').read().split('\n')
    a = [i for i in a if i != '']
    return a

def writeFile(data, f='groupMembers.json'):
    try:
        print('trying to write into existing file')
        a = open(f, 'a', encoding='utf8')
        print('success')
    except:
        print('making new result file: %s'%f)
        a = open(f, 'w', encoding='utf8')
    print(data, file=a)
    a.close()


def loadVkCode(f):
    code = open(f, encoding='utf8').read()
    code = code.replace('+', '%20%2B')
    return code


def collectFromList(list_of_lists):
    ## берет на вход список списков
    ## возвращает сумму этих списков
    result = []
    for i in list_of_lists:
        if type(i) == list:
            result += collectFromList(i)
        else:
            result.append(i)
    return result


def vk_makeRequest(method, access_token, **kwargs):
    request = 'https://api.vk.com/method/%s'%method
    if kwargs:
        request += '?'
        for kwarg in kwargs:
            request += '%s=%s&'%(kwarg, kwargs[kwarg])
    request += 'access_token=%s'%access_token
    return request


def vk_callRequest(request):
    j = None
    while not j:
        try:
            r = req.get(request)
            t = r.text
            j = json.loads(t)
        except Exception as e:
            print('vk cll failed: %s'%e)
            continue
    return j


def getMembersFromReq(req):
    res = [req[0], []]
    for i in req[1]:
        res[1] += i['users']
    return res


def callVkApi(method, access_token, **kwargs):
    request = vk_makeRequest(method, access_token, **kwargs)
    response = vk_callRequest(request)

    if 'error' in response:
        if response['error']['error_code'] == 15:
            print('no access to group')
            response = {'count':0,'users':[]}
        else:
            while 'error' in response:
                time.sleep(0.333333)
                print('calling again...')
                response = vk_callRequest(request)
    try:
        response = response['response']
    except Exception as e:
        # print(e)
        response = response
    # print('response: ', response)
    return response


def getGroupUsers(groupid, access_token):
    # print('\n%s'%groupid)
    ## берет на вход id группы вк
    ## возвращает список id пользователей этой группы
    members_gl = []
    offset = 0 
    g = callVkApi('groups.getMembers', access_token, group_id=groupid,offset=offset)
    # print(g)
    g = g['count']
    strt = datetime.datetime.now()
    if g == 0:
        print('api method returned no users. perhaps group is blocked\n')
        return []
    else:
        while offset < g + 25000:
            code = loadVkCode('getAllUsersFromOneGroup.vkcode')
            code = code%(offset, groupid)
            returned = callVkApi('execute', access_token, code='%s'%code)
            offset_ = returned[0]
            members = returned[1]
            members = [i['users'] for i in members if i['users'] != []]
            members = collectFromList(members)
            members_gl += members
            offset = offset_
            time.sleep(0.3333333)
            sys.stdout.write('\rfrom group %s collected %s users out of %s'%(groupid, len(collectFromList(members_gl)), g))
            sys.stdout.flush()
        fnsh = datetime.datetime.now()
        print('\nspent time: %s\n'%(fnsh-strt))
        return collectFromList(members_gl)


if __name__ == '__main__':

    flist = ['суицид список групп.txt']
    for f in flist:
        print(f, '\n')
        dname = f[:-4]
        try:
            os.mkdir(os.getcwd() + '/folders/' + dname)
        except:
            print('dir %s exists'%dname)
        gr = loadListFromFile(f)
        gr = [int(i) for i in gr]
        for g in gr:
            u = getGroupUsers(g, loadListFromFile('access_token')[0])
            e = open(os.getcwd() + '/folders/%s/%s.txt'%(dname, g), 'w', encoding='utf8')
            for i in u:
                print(i, file=e)
            e.close()
