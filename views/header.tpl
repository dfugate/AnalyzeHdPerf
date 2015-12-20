<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <title>{{title}}</title>

        <!-- Bootstrap -->
        <link rel="stylesheet" href="/static/css/bootstrap.min.css">
        <link rel="stylesheet" href="/static/css/bootstrap-theme.min.css">
        <script src="/static/js/jquery-2.1.4.min.js"></script>
        <script src="/static/js/bootstrap.min.js"></script>
    </head>
    <body style="padding-top: 50px;">
        <div class="container">
            <nav class="navbar navbar-inverse navbar-fixed-top">
                <div class="container">
                    <div class="navbar-header">
                        <a class="navbar-brand" onclick="window.open('http://www.linkedin.com/in/davidfugate');return false;">
                            <img src="/static/img/me.jpg"
                                 width="30" height="30"
                                 alt="David Wayne Fugate"
                                 class="img-circle" style="cursor: pointer;"/>
                        </a>
                    </div>

                    <div class="collapse navbar-collapse">
                        <ul class="nav navbar-nav">
                            <li class="active"><p class="navbar-text">Hard Drive Performance Analyzer</p></li>
                            <li><a href="/">
                                    <span class="glyphicon glyphicon-home" aria-hidden="true"> Home</span>
                                </a>
                            </li>
                            <li><a href="/status">
                                    <span class="glyphicon glyphicon-dashboard" aria-hidden="true"> Status</span>
                                </a>
                            </li>
                            <li><a href="/report">
                                    <span class="glyphicon glyphicon-stats" aria-hidden="true"> Report</span>
                                </a>
                            </li>
                            <li><a href="/logs">
                                    <span class="glyphicon glyphicon-list" aria-hidden="true"> Logs</span>
                                </a>
                            </li>
                        </ul>
                        <ul class="nav navbar-nav navbar-right">
                            <li><a href="/about">
                                <span class="glyphicon glyphicon-user" aria-hidden="true"> About</span>
                                </a>
                            </li>
                        </ul>
                    </div>


                </div>
            </nav>