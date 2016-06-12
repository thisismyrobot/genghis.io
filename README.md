# The project formally known as GengisIO

## NOTE

This is a snapshot of a project I worked on for a while.

It combined a web application and and Android app, over websockets, to allow
for direct Python-based robot programming (and control) of the Sphero robot in
a web-based IDE without installing any drivers.

The back-end was a Google App Engine application (later a flask app)
communicating via a web application and websockets to the server, and a mobile
Android application using websockets (in a WebView) to bridge to the Sphero
robot using bluetooth.

The Python dev in the browser was supported by empythoned.

I abandoned this project due to the complexity and difficulty I was
experiencing "selling" the multiple "problems" it solved. I figure the right
thing to do is to share it with the world :)

## Idea

Make programming interesting robots easy.

## Detail

Programming interesting (non-predictable and interactive) robot behaviours is
hard. So is programming in general if you haven't done it before.

This project aims to:
 * Simplify the learning curve into programming - without removing the amazing
   power of Python.
 * Allow for the creation of non-deterministic but reactive robot behaviours
   without a physics degree.
