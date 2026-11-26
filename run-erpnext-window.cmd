@echo off
title Digitbox Manufacturing ERP - Startup
powershell -NoExit -ExecutionPolicy Bypass -File "%~dp0start-erpnext.ps1" %*
