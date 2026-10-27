rmdir /Q /S ..\alyvix\ide\server\static\alyvix-ui

CMD /C node_modules\.bin\ng build --prod --sourceMap=true --configuration production 

move dist\alyvix-ui ..\alyvix\ide\server\static\alyvix-ui