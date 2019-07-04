rmdir /Q /S ..\alyvix\ide\server\static\alyvix-ui

CMD /C ng build --prod --sourceMap=true --configuration production 

move dist\alyvix-ui ..\alyvix\ide\server\static\alyvix-ui