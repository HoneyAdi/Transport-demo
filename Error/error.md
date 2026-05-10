TypeError
TypeError: object of type 'generator' has no len()

Traceback (most recent call last)
File "C:\Users\hp\AppData\Local\Programs\Python\Python311\Lib\site-packages\flask\app.py", line 2213, in __call__
return self.wsgi_app(environ, start_response)
       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "C:\Users\hp\AppData\Local\Programs\Python\Python311\Lib\site-packages\flask\app.py", line 2193, in wsgi_app
response = self.handle_exception(e)
           ^^^^^^^^^^^^^^^^^^^^^^^^
File "C:\Users\hp\AppData\Local\Programs\Python\Python311\Lib\site-packages\flask\app.py", line 2190, in wsgi_app
response = self.full_dispatch_request()
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "C:\Users\hp\AppData\Local\Programs\Python\Python311\Lib\site-packages\flask\app.py", line 1486, in full_dispatch_request
rv = self.handle_user_exception(e)
     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^Open an interactive python shell in this frame
File "C:\Users\hp\AppData\Local\Programs\Python\Python311\Lib\site-packages\flask\app.py", line 1484, in full_dispatch_request
rv = self.dispatch_request()
     ^^^^^^^^^^^^^^^^^^^^^^^
File "C:\Users\hp\AppData\Local\Programs\Python\Python311\Lib\site-packages\flask\app.py", line 1469, in dispatch_request
return self.ensure_sync(self.view_functions[rule.endpoint])(**view_args)
       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "d:\HONEY\Projects\transport-master\webapp.py", line 461, in wrapper
return func(*args, **kwargs)
       ^^^^^^^^^^^^^^^^^^^^^
File "d:\HONEY\Projects\transport-master\webapp.py", line 10430, in customer_communications
return render_template(
       
File "C:\Users\hp\AppData\Local\Programs\Python\Python311\Lib\site-packages\flask\templating.py", line 151, in render_template
return _render(app, template, context)
       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "C:\Users\hp\AppData\Local\Programs\Python\Python311\Lib\site-packages\flask\templating.py", line 132, in _render
rv = template.render(context)
     ^^^^^^^^^^^^^^^^^^^^^^^^
File "C:\Users\hp\AppData\Local\Programs\Python\Python311\Lib\site-packages\jinja2\environment.py", line 1295, in render
self.environment.handle_exception()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "C:\Users\hp\AppData\Local\Programs\Python\Python311\Lib\site-packages\jinja2\environment.py", line 942, in handle_exception
raise rewrite_traceback_stack(source=source)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "d:\HONEY\Projects\transport-master\templates\customers\communications.html", line 1, in top-level template code
{% extends 'base.html' %}
File "d:\HONEY\Projects\transport-master\templates\base.html", line 696, in top-level template code
{% block content %}{% endblock %}
File "d:\HONEY\Projects\transport-master\templates\customers\communications.html", line 49, in block 'content'
<h5 class="mb-0">{{ communications|selectattr('status', equalto='open')|length or 0 }}</h5>
TypeError: object of type 'generator' has no len()
The debugger caught an exception in your WSGI application. You can now look at the traceback which led to the error.
To switch between the interactive traceback and the plaintext one, you can click on the "Traceback" headline. From the text traceback you can also create a paste of it. For code execution mouse-over the frame you want to debug and click on the console icon on the right side.

You can execute arbitrary Python code in the stack frames and there are some extra helpers available for introspection:

dump() shows all variables in the frame
dump(obj) dumps all that's known about the object
Brought to you by DON'T PANIC, your friendly Werkzeug powered traceback interpreter.