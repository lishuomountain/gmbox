var c=window,d=document;
function f(b,a)
{
    return b.width=a
}
function g(b,a)
{
    return b.height=a
}
var h="clientWidth",i="getElementById",j="location",k="style",l="body",m="clientHeight",n="documentElement",o="http://www.google.cn/music/top100/",p=o+"lyrics",q=o+"musicdownload",r=o+"player_page",s="Top100 Online Player";
function t(b)
{
    var a=d[i](b);
    if(a)if(c.innerHeight&&c.innerWidth)
    {
        f(a,c.innerWidth);g(a,c.innerHeight)
    }
    else if(d[n]&&d[n][m]&&d[n][h])
    {
        f(a,d[n][h]);
        g(a,d[n][m])
    }
    else if(d[l][m]&&d[l][h])
    {
        f(a,d[l][h]);
        g(a,d[l][m])
    }
}
function u()
{
    var b=d[i]("lyrics-iframe"),a=p+c[j].search;
    if(b&&b.src!=a)b.src=a;t("lyrics-iframe")
}
function v()
{
    var b=d[i]("download-iframe"),
        a=q+c[j].search;
    if(b&&b.src!=a)
        b.src=a;
    t("download-iframe")
}
function w()
{
    c.name=s;c.document.title=s;
    var b=d[i]("player-iframe"),a=r+c[j].search+c[j].hash;
    if(b&&b.src!=a)b.src=a;
    t("player-iframe");
    var y=c.setInterval(x,500);
    function x()
    {
        if(b.contentWindow.length>=4)
        {
            c.clearInterval(y);
            var e=d.createElement("iframe");
            e.setAttribute("frameborder", " 0");
            g(e[k],"0");
            f(e[k],"0");
            e[k].top="0";
            e[k].left="0";
            e[k].position="absolute";
            e[k].zIndex=-1;
            e[k].display="none";
            e.src="";
            d[l].appendChild(e)
        }
    }
    c[j].hash="#loaded"
}
var _onloadLyricsPage=u, _onloadDownloadPage=v, _onloadPlayerPage=w, _onWindowResize=t;
