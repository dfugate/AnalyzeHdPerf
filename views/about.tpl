% include('header.tpl', title='HDPA - About')

<h1>
    About
</h1>
<hr />

<div class="well">
    <p>
    <i>Hard Drive Performance Analyzer</i> is open source and the full source code is available on my
    <a onclick="window.open('https://github.com/dfugate/AnalyzeHdPerf'); return false;" style="cursor: pointer;">
    GitHub account</a>.
    </p>

    <h4>Key Features & Technologies</h4>
    <ul>
        <li>Both server and client configuration parameters are settable from the command-prompt.</li>
        <li>Test clients run file-creation tasks for a designated amount of time and then shutdown.</li>
        <li>The server owns instantiation of a test client and kicks it off via SSH. Also, the server is capable of
            handling multiple concurrent test clients running either locally or remotely (if SSH has been configured
            appropriately).</li>
        <li>Test clients communicate performance data (e.g., file rollover time, total CPU utilization, and <b>new</b>
            memory consumption) to the server via RESTful services. These clients are also expected to send so-called
            “heartbeat” notifications at designated intervals.</li>
        <li>A server thread monitors the health of it’s clients through these heartbeats and “knows” when they’ve died
            suddenly.</li>
        <li>Virtually everything is logged – server and client. Clients send (most) of their logs to the server which
            are then rendered on the “Logs” page.</li>
        <li>The server’s front-end is powered by the (Python) bottle framework and Bootstrap. Although this application
            is based on Python 2.7, it uses a port of 3.4’s <i>statistics</i> module instead of <i>NumPy</i> which I
            deemed too heavyweight.</li>
        <li>The test clients use Google’s <i>psutil</i> package to glean performance data.
    </ul>

</div>

% include('footer.tpl')