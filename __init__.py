# -*- coding: utf-8 -*-

from main import CheckAquisicao  


def name():
    return "check aquisição"
def description():
    return "verifica se a aquisição está sendo feito na área certa"
def version():
    return "Version 0.1"

def classFactory(iface):
    return CheckAquisicao(iface)

def qgisMinimumVersion():
    return "2.0"
def author():
    return "jossan costa"
def email():
    return "me@hotmail.com"
def icon():
    return "icon.png"

## any other initialisation needed
