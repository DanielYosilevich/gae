
from google.appengine.ext import ndb

import webapp2
import json

class MainPage(webapp2.RequestHandler):
   def get(self): 
    self.response.out.write("""
    <html>
    <head>
        <title>Backend Challenge</title>
        <link rel="stylesheet" type="text/css" href="/css/main.css" />    
    </head>
    <body>
      <header>
         <h2> Backend Challenge </h2>
         <hr>
      </header>
      <main>
         <div class = forms-wrapper>
            <span>SET</span>
            <div class = form-container>
               <form action="/set" method="get">
                  <input name="name" placeholder = "Name" required>
                  <input name="value" placeholder = "Value" required>
                  <input type="submit" value="Query">
               </form>
            </div>
            <span>UNSET</span>
            <div class = form-container>
               <form action="/unset" method="get">
                  <input name="name" placeholder = "Name" required>
                  <input type="submit" value="Query">
               </form>
            </div>
            <span>GET</span>
            <div class = form-container>
               <form action="/get" method="get">
                  <input name="name" placeholder = "Name" required>
                  <input type="submit" value="Query">
               </form>
            </div>
            <span>NUM_EQUAL_TO</span>
            <div class = form-container>
               <form action="/numequalto" method="get">
                  <input name="value" placeholder = "Value" required>
                  <input type="submit" value="Query">
               </form>
            </div>
            <div class = form-container>
               <form action="/entries" method="get">
                  <input type="submit" value="Entries List">
               </form>
            </div>
            <div class = form-container>
               <form action="/undo" method="get">
                  <input type="submit" value="Undo">
               </form>
            </div>
            <div class = form-container>
               <form action="/undotracker" method="get">
                  <input type="submit" value="Undo Tracker">
               </form>
            </div>
            <div class = form-container>
               <form action="/redo" method="get">
                  <input type="submit" value="Redo">
               </form>
            </div>
            <div class = form-container>
               <form action="/redotracker" method="get">
                  <input type="submit" value="Redo Tracker">
               </form>
            </div>
            <div class = form-container>
               <form action="/clean" method="get">
                  <input type="submit" value="Clean">
               </form>
            </div>
         </div>
      </main>
    </body>
    </html>""" )
  
class Item(ndb.Model):
  name = ndb.StringProperty()
  value = ndb.StringProperty()

class ActionU(ndb.Model):
   item_id = ndb.StringProperty()
   item_val_prev = ndb.StringProperty()
   item_val_curr = ndb.StringProperty()
   op = ndb.StringProperty()
   date = ndb.DateTimeProperty(auto_now_add=True)

class ActionR(ndb.Model):
   item_id = ndb.StringProperty()
   item_val_prev = ndb.StringProperty()
   item_val_curr = ndb.StringProperty()
   op = ndb.StringProperty()
   date = ndb.DateTimeProperty(auto_now_add=True)   

class SetPage(webapp2.RequestHandler):
  def get(self):
    q = ActionR.query().fetch()  
    list_of_keys = ndb.put_multi(q)  
    ndb.delete_multi(list_of_keys) 
    name = self.request.get('name')
    value = self.request.get('value')
    key = ndb.Key('Item',name)
    item = key.get()
    item_id = name
    if not item:
        op = 'INITIAL_SET'
        item_val_prev = 'NONE'
    else:
        op = 'SET'  
        item_val_prev = item.value
    action = ActionU(op = op,item_id = item_id,item_val_prev = item_val_prev ,item_val_curr = value)        
    action.put()   
    item = Item(id=name)
    item.name = name
    item.value = value
    res = map(str,name + ' was set to: ' + value)
    item.put()
    self.response.write("""
      <html>
      <head>
         <script>
           var res = %s
         </script>
         <title>Set</title>
         <link rel="stylesheet" type="text/css" href="/css/main.css" />    
      </head>
      <body>
         <header>
            <h2>Set</h2>
            <hr>
         </header>
         <main>
            <div data-v="item"></div>
            <hr>
            <br>
            <form action="/" method="get">
               <div><input type="submit" value="Home"></div>
            </form>
         </main>
         <script>
            document.querySelector('[data-v = "item"]').innerHTML = res.join('');
         </script>
      </body>
      </html>""" % (res))

class UnsetPage(webapp2.RequestHandler):
  def get(self):
   q = ActionR.query().fetch()  
   list_of_keys = ndb.put_multi(q)  
   ndb.delete_multi(list_of_keys)  
   name = self.request.get('name')
   key = ndb.Key('Item',name)
   item = key.get() 
   if not item:
      res = map(str,'No Entry with name: ' + name + '!')
   else:
      action = ActionU(op = 'UNSET',item_id = name,item_val_prev = item.value ,item_val_curr = 'NONE')        
      action.put()  
      item.key.delete()
      res = map(str,'Entry with name: ' + name  + ' was sucessfully removed!')
   self.response.write("""
      <html>
      <head>
         <script>
           var res = %s
         </script>
         <title>Unset</title>
         <link rel="stylesheet" type="text/css" href="/css/main.css" />    
      </head>
      <body>
         <header>
            <h2>Unset</h2>
            <hr>
         </header>
         <main>
            <div data-v="item"></div>
            <hr>
            <br>
            <form action="/" method="get">
               <div><input type="submit" value="Home"></div>
            </form>
         </main>
         <script>
            document.querySelector('[data-v = "item"]').innerHTML = res.join('');
         </script>
      </body>
      </html>""" % (res))

class GetPage(webapp2.RequestHandler):
   def get(self):
      q = ActionR.query().fetch()  
      list_of_keys = ndb.put_multi(q)  
      ndb.delete_multi(list_of_keys)
      name = self.request.get('name')
      q = Item.query(Item.name == name).fetch()
      res = map(str,q) 
      nam = map(str,name)
      self.response.write("""
      <html>
      <head>
         <script>
           var res = %s
           var nam = %s
           let val
           if(res.length) val = res.join('').split(',')[3].slice(8,-1)
           else val = 'NONE'
         </script>
         <title>Get</title>
         <link rel="stylesheet" type="text/css" href="/css/main.css" />    
      </head>
      <body>
         <header>
            <h2>Get</h2>
            <hr>
         </header>
         <main>
            <div data-v="item"></div>
            <hr>
            <br>
            <form action="/" method="get">
               <div><input type="submit" value="Home"></div>
            </form>
         </main>
         <script>
            document.querySelector('[data-v = "item"]').innerHTML = 
            `Name <span>${nam.join('')}</span> matches value <span>${val}</span>!`;
         </script>
      </body>
      </html>""" % (res,nam))     
     

class NumEqualToPage(webapp2.RequestHandler):
   def get(self):
      q = ActionR.query().fetch()  
      list_of_keys = ndb.put_multi(q)  
      ndb.delete_multi(list_of_keys)
      value = self.request.get('value')
      q = Item.query(Item.value == value).fetch()
      res = map(str,q) 
      val = map(str,value)
      self.response.write("""
      <html>
      <head>
         <script>
           var res = %s
           var val = %s
         </script>
         <title>NumEqualTo</title>
         <link rel="stylesheet" type="text/css" href="/css/main.css" />    
      </head>
      <body>
         <header>
            <h2>NumEqualTo</h2>
            <hr>
         </header>
         <main>
            <div data-v="item"></div>
            <hr>
            <br>
            <form action="/" method="get">
               <div><input type="submit" value="Home"></div>
            </form>
         </main>
         <script>
            document.querySelector('[data-v = "item"]').innerHTML = 
            `Value <span>${val.join('')}</span> matched <span>${res.length}</span> entries!`;
         </script>
      </body>
      </html>""" % (res,val))     

class EntriesPage(webapp2.RequestHandler):
  def get(self):
   q = Item.query().fetch()
   a = map(str, q)
   self.response.write("""
   <html>
   <head>
      <script>
      var a = %s 
      </script>
      <title>Database entries</title>
      <link rel="stylesheet" type="text/css" href="/css/main.css" />    
   </head>
   <body>
      <header>
         <h2> Database Entries </h2>
         <hr>
      </header>
      <main>
         <div data-v = "list"></div>
         <form action="/" method="get">
            <div><input type="submit" value="Home"></div>
         </form>
      </main>
      <script>
         let st = `<ul>`;
         a.forEach((el) => st += `<li> ${el} </li>`)
         st += `</ul> <hr>`
         document.querySelector('[data-v = "list"]').innerHTML = st;
      </script>
   </body>
   </html>""" % (a))


class UndoPage(webapp2.RequestHandler):
  def get(self):
   q = ndb.gql("SELECT * FROM ActionU ORDER BY date DESC")
   row = q.get()    
   if not row:
       o = json.dumps('NONE') 
       num = json.dumps('NONE') 
       prev = json.dumps('NONE') 
       curr = json.dumps('NONE') 
   else:
      action = ActionR(op = row.op,item_id = row.item_id,item_val_prev = row.item_val_prev ,item_val_curr = row.item_val_curr)        
      action.put()  
      o = json.dumps(row.op) 
      prev = json.dumps(row.item_val_prev) 
      curr = json.dumps(row.item_val_curr) 
      num = json.dumps(row.item_id)    
      if row.op == 'INITIAL_SET':
         key = ndb.Key('Item',row.item_id)
         item = key.get() 
         item.key.delete()
      else:
         item = Item(id=row.item_id)
         item.name = row.item_id
         item.value = row.item_val_prev
         item.put()  
      key = row.key
      action = key.get() 
      action.key.delete()
   self.response.write("""
   <html>
   <head>
      <script>
      var o = %s 
      var num = %s 
      var prev = %s 
      var curr = %s 
      </script>
      <title>Undo</title>
      <link rel="stylesheet" type="text/css" href="/css/main.css" />    
   </head>
   <body>
      <header>
         <h2> Undo  </h2>
         <hr>
      </header>
      <main>
         <div data-v = "list"></div>
         <br>
         <form action="/" method="get">
            <div><input type="submit" value="Home"></div>
         </form>
      </main>
      <script>
         document.querySelector('[data-v = "list"]').innerHTML = 
             (o !== 'NONE') ?  ` Operation ${o} ${num} ${curr} was undone!` : 'Nothing to Undo!'
      </script>
   </body>
   </html>""" % (o,num,prev,curr))   

class UndoTrackerPage(webapp2.RequestHandler):
  def get(self):
   q = ActionU.query().fetch()
   a = map(str, q)  
   self.response.write("""
   <html>
   <head>
      <script>
      var a = %s 
      </script>
      <title>Undo Tracker</title>
      <link rel="stylesheet" type="text/css" href="/css/main.css" />    
   </head>
   <body>
      <header>
         <h2> Undo Tracker </h2>
         <hr>
      </header>
      <main>
         <div data-v = "list"></div>
         <form action="/" method="get">
            <div><input type="submit" value="Home"></div>
         </form>
      </main>
      <script>
         let st = `<ul>`;
         a.forEach((el) => st += `<li> ${el} </li>`)
         st += `</ul> <hr>`
         document.querySelector('[data-v = "list"]').innerHTML = st;
      </script>
   </body>
   </html>""" % (a))   

class RedoPage(webapp2.RequestHandler):
  def get(self):
   q = ndb.gql("SELECT * FROM ActionR ORDER BY date DESC")
   row = q.get()    
   if not row:
       o = json.dumps('NONE') 
       num = json.dumps('NONE') 
       prev = json.dumps('NONE') 
       curr = json.dumps('NONE') 
   else:
      o = json.dumps(row.op) 
      prev = json.dumps(row.item_val_prev) 
      curr = json.dumps(row.item_val_curr) 
      num = json.dumps(row.item_id)    
      item = Item(id=row.item_id)
      item.name = row.item_id
      item.value = row.item_val_curr
      item.put()  
      key = row.key
      action = key.get() 
      action.key.delete()
   self.response.write("""
   <html>
   <head>
      <script>
      var o = %s 
      var num = %s 
      var prev = %s 
      var curr = %s 
      </script>
      <title>Redo</title>
      <link rel="stylesheet" type="text/css" href="/css/main.css" />    
   </head>
   <body>
      <header>
         <h2> Redo  </h2>
         <hr>
      </header>
      <main>
         <div data-v = "list"></div>
         <br>
         <form action="/" method="get">
            <div><input type="submit" value="Home"></div>
         </form>
      </main>
      <script>
         document.querySelector('[data-v = "list"]').innerHTML = 
             (o !== 'NONE') ?  ` Performed backroll to operation ${o} ${num} ${curr}!` : 'Nothing to Redo!'
      </script>
   </body>
   </html>""" % (o,num,prev,curr))   

class RedoTrackerPage(webapp2.RequestHandler):
  def get(self):
   q = ActionR.query().fetch()
   a = map(str, q)  
   self.response.write("""
   <html>
   <head>
      <script>
      var a = %s 
      </script>
      <title>Redo Tracker</title>
      <link rel="stylesheet" type="text/css" href="/css/main.css" />    
   </head>
   <body>
      <header>
         <h2> Redo Tracker </h2>
         <hr>
      </header>
      <main>
         <div data-v = "list"></div>
         <form action="/" method="get">
            <div><input type="submit" value="Home"></div>
         </form>
      </main>
      <script>
         let st = `<ul>`;
         a.forEach((el) => st += `<li> ${el} </li>`)
         st += `</ul> <hr>`
         document.querySelector('[data-v = "list"]').innerHTML = st;
      </script>
   </body>
   </html>""" % (a))     
   
class CleanPage(webapp2.RequestHandler):
  def get(self):
   q = Item.query().fetch()  
   list_of_keys = ndb.put_multi(q)  
   ndb.delete_multi(list_of_keys)
   q = ActionU.query().fetch()  
   list_of_keys = ndb.put_multi(q)  
   ndb.delete_multi(list_of_keys)
   q = ActionR.query().fetch()  
   list_of_keys = ndb.put_multi(q)  
   ndb.delete_multi(list_of_keys)
   self.response.write("""
   <html>
   <head>
      <title>Clean Database</title>
      <link rel="stylesheet" type="text/css" href="/css/main.css" />    
   </head>
   <body>
      <header>
         <h2>Clean Database </h2>
         <hr>
      </header>
      <main>
         <h3>Removed All Database Entries!</h3>
         <form action="/" method="get">
            <div><input type="submit" value="Home"></div>
         </form>
      </main>
   </body>
   </html>""" )

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/set', SetPage),
    ('/unset', UnsetPage),
    ('/get', GetPage),
    ('/numequalto', NumEqualToPage),
    ('/entries', EntriesPage),
    ('/undo', UndoPage),
    ('/undotracker', UndoTrackerPage),
    ('/redo', RedoPage),
    ('/redotracker', RedoTrackerPage),
    ('/clean', CleanPage)
], debug=True)
