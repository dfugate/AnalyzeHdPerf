% include('header.tpl', title='HDPA - Home')

<h1>
    Home
</h1>
<hr />

<div class="well">
    <p>
    <i>Hard Drive Performance Analyzer</i> is a tool I developed in my (limited) free time to
    reacquaint myself with Python after nearly a five-year hiatus. In short, it's a distributed
    hard drive benchmark in which the server spawns the performance tests on client machines via
    SSH. These clients then report their results back using REST services provided by this server.
    </p>
</div>

% include('footer.tpl')