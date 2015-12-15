% include('header.tpl', title='HDPA - About')

<h1>
    About
</h1>
<hr />

<div class="well">
    <p>
    <i>Hard Drive Performance Analyzer</i> is open source and the full source code can be found on my
    <a onclick="window.open('https://github.com/dfugate/AnalyzeHdPerf'); return false;" style="cursor: pointer;">
    GitHub account</a>.
    </p>

    <h4>Key Technologies</h4>
    <ul>
        <li>Back-end is based on Python 2.7, the <i>psutil</i> module, and SSH.</li>
        <li>Configured via the <i>argparse</i> module.</li>
        <li>Front-end uses the <i>bottle</i> framework, <i>Bootstrap</i>, and <i>D3.js</i>.</li>
    </ul>

    <h4>Features</h4>
    <ul>
        <li>TODO</li>
    </ul>

</div>

% include('footer.tpl')