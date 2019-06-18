rmdir /Q /S ..\alyvix\ide\server\static\alyvix-ui

ng build --prod --configuration production 

move dist\alyvix-ui ..\alyvix\ide\server\static\alyvix-ui