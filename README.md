# UAV-HiRAP
Unmanned Aerial Vehicles - High Resolution imagery Analysis Platform (UAV-HiRAP), is an open-source, web-based platform which provides service for image classification.    

This is developed in Python-Flask Framework, and released at: https://www.uav-hirap.org. Also a standalone version based on pyqt will be developed in the future.    

This project is published at:    
> Haozhou Wang, Dong Han, Yue Mu, Lina Jiang, Xueling Yao, Yongfei Bai, Qi Lu, Feng Wang*. 2019. Landscape-level vegetation classification and fractional woody and herbaceous vegetation cover estimation over the dryland ecosystems by unmanned aerial vehicle platform. Agricultural and Forest Meteorology, 278: 107665 DOI: [10.1016/j.agrformet.2019.107665](https://www.sciencedirect.com/science/article/pii/S0168192319302734?via%3Dihub)    

if you benefit from this project in your research, welcome to cite our paper!

# Folder Tree (In Chinese)
|- UAV-HiRAP    
  |- app/    
  |  |- auth/ <font color='red'>——用户登陆与注册蓝本</font>    
  |  |  |- \_\_init\_\_.py   <font color='blue'>——定义auth路由蓝本</font>    
  |  |  |- forms.py   <font color='blue'>——登陆与注册表单</font>    
  |  |  |- views.py   <font color='blue'>——对不同网址作响应的视图函数</font>    
  |  |- main/ <font color='red'>——主页及静态网页蓝本</font>    
  |  |  |- \_\_init\_\_.py    
  |  |  |- errors.py    
  |  |  |- form.py    
  |  |  |- views.py   
  |  |- proj <font color='red'>——用户项目蓝本</font>    
  |  |  |- \_\_init\_\_.py   <font color='blue'>——定义项目路由</font>    
  |  |  |- decisiontree.py   <font color='blue'>——决策树核心算法</font>    
  |  |  |- route_design.py   <font color='blue'>——决策树核心算法</font>    
  |  |  |- forms.py    
  |  |  |- views.py     
  |  |- templates/ <font color='orange'>——网页模板文件</font>    
  |  |  |- auth/   <font color='red'>——用户登陆与注册蓝本用到的网页</font>    
  |  |  |  |- email/   <font color='blue'>——发送的email模板</font>    
  |  |  |  |  |- confirm.html   <font color='blue'>——确认邮件</font>    
  |  |  |  |  |- confirm.txt    
  |  |  |  |  |- userinfo.html   <font color='blue'>——发送给管理员的新注册用户信息</font>    
  |  |  |  |  |- userinfo.txt    
  |  |  |  |- login.html   <font color='blue'>——登陆界面</font>    
  |  |  |  |- register.html   <font color='blue'>——注册界面</font>    
  |  |  |  |- unconfirmed.html   <font color='blue'>——未确认拦截界面</font>    
  |  |  |  |- profile.html   <font color='blue'>——用户简历界面</font>    
  |  |  |- proj/   <font color='red'>——用户项目蓝本用到的网页</font>    
  |  |  |  |- base.html   <font color='blue'>——项目控制界面</font>    
  |  |  |  |- dtc*.html   <font color='blue'>——决策树分类</font>    
  |  |  |  |- rd*.html   <font color='blue'>——航线规划</font>    
  |  |  |  |- guide.html   <font color='blue'>——用户手册(老版，待更新)</font>    
  |  |  |  |- seg*.html   <font color='blue'>——单木分割模块(开发中)</font>    
  |  |  |- 404.html   <font color='blue'>——404错误网站</font>    
  |  |  |- 500.html   <font color='blue'>——500错误网站</font>    
  |  |  |- base.html   <font color='blue'>——基模板</font>    
  |  |  |- index.html   <font color='blue'>——网站首页</font>    
  |  |  |- developing.html   <font color='blue'>——开发中</font>    
  |  |  |- user.html   <font color='blue'>——用户界面（测试用，现在闲置）</font>    
  |  |- static/   <font color='orange'>——静态文件</font>      
  |  |  |- UserData/   <font color='blue'>——用户数据储存位置</font>    
  |  |  |- folder*/   <font color='blue'>——与项目相对应的</font>    
  |  |- translations/ <font color='green'>——多语言模块（待完善，可忽略）</font>    
  |  |- \_\_init\_\_.py   <font color='blue'>——把上面auth、dtc、main三个蓝本，邮件发送，数据库读写等整合在一起</font>    
  |  |- email.py   <font color='blue'>——发送电子邮件</font>    
  |  |- models.py   <font color='blue'>——数据库模型</font>    
  |- migrations/  <font color='green'>——数据库迁移缓存（模板，可忽略）</font>    
  |- tests/   <font color='green'>——测试工具箱（模板，可忽略）</font>    
  |  |- \_\_init\_\_.py    
  |  |- test\*.py    
  |- venv/  <font color='blue'>——Python虚拟环境</font>    
  |- requirements.txt  <font color='blue'>——需要的python包和版本，便于在其他电脑上生成同样的虚拟环境</font>    
  |- config.py  <font color='blue'>——网站总配置文件</font>    
  |- manage.py  <font color='blue'>——用于启动程序以及其他的程序任务</font>    
  |- email_config.txt <font color='blue'>——储存邮件发送的账户及密码</font>    