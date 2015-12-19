% include('header.tpl', title='HDPA - Home')

<h1>
    Home
</h1>
<hr />

<div class="well">
    <p>
    <i>Hard Drive Performance Analyzer</i> is a small tool
    <a onclick="window.open('http://www.linkedin.com/in/davidfugate');return false;" style="cursor: pointer;">I</a> developed in my
    free time to reacquaint myself with Python after nearly a five-year hiatus. In short, it's a distributed hard drive
    benchmark in which the server spawns performance tests on (potentially) remote client machines using SSH. These
    clients then report their results back using REST services provided by this server. More details about this tool
    can be seen on the <a href="/about">About</a> page.
    </p>
</div>

% include('footer.tpl')