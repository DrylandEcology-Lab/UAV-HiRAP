# UAV-HiRAP
Unmanned Aerial Vehicles - High Resolution Imagery Analysis Platform

### Folder Tree
|- UAV-HiRAP
&emsp;&emsp;|- app/
&emsp;&emsp;&emsp;&emsp;|- auth/ <font color='blue'>----User login and regist function</font>
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|- \_\_init\_\_.py
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|- forms.py
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|- views.py
&emsp;&emsp;&emsp;&emsp;|- dtc <font color='blue'>----Decision Tree Classifer codes folder</font>
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|- UAV-HiRAP4Linux.py
&emsp;&emsp;&emsp;&emsp;|- main/ <font color='blue'>----Index and frame folder</font>
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|- \_\_init\_\_.py
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|- errors.py
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|- form.py
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|- views.py
&emsp;&emsp;&emsp;&emsp;|- templates/ <font color='blue'>----*.html folder</font>
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|- auth/
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|- email/
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|- confirm.html
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|- confirm.txt
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|- login.html
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|- register.html
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|- unconfirmed.html
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|- dtc/
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|- index.html
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|- bdd/
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|- index.html
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|- 404.html
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|- 500.html
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|- base.html
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|- index.html
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|- user.html
&emsp;&emsp;&emsp;&emsp;|- static/
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|- ExamplePic/
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;|- home.ico
&emsp;&emsp;&emsp;&emsp;|- \_\_init\_\_.py
&emsp;&emsp;&emsp;&emsp;|- email.py
&emsp;&emsp;&emsp;&emsp;|- models.py
&emsp;&emsp;|- migrations/
&emsp;&emsp;|-tests/
&emsp;&emsp;&emsp;&emsp;|- \_\_init\_\_.py
&emsp;&emsp;&emsp;&emsp;|- test\*.py
&emsp;&emsp;|- venv/
&emsp;&emsp;|- requirements.txt
&emsp;&emsp;|- config.py
&emsp;&emsp;|- manage.py
&emsp;&emsp;|- email_config.txt <font color='blue'>----save email sender account username and password</font>