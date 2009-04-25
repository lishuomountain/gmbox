var c=window,d=document;
function f(b,a)
{
    return b.width=a
}
function g(b,a)
{
    return b.height=a
}
var h="clientWidth",i="getElementById",j="location",k="style",l="body",m="clientHeight",n="documentElement",o="http://www.google.cn/music/top100/",p=o+"lyrics",q="http://www.google.cn/music/top100/musicdownload",r=o+"player_page",s="Top100 Online Player";
function t(frame_type)
{
    var a=document["getElementById"](frame_type);
    if(a)
        if(window.innerHeight&&window.innerWidth)
        {
            //设置download窗口大小
            f(a,window.innerWidth);
            g(a,window.innerHeight)
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
    var b=d[i]("lyrics-iframe"),a=p+window[j].search;
    if(b&&b.src!=a)b.src=a;t("lyrics-iframe")
}
function _onloadDownloadPage()
{
    var b=document["getElementById"]("download-iframe"),
        donwload_url="http://www.google.cn/music/top100/musicdownload"+window["location"].search;
    if(b&&b.src!=download_url)
        b.src=downlaod_url;
    t("download-iframe")
}
function w()
{
    window.name=s;window.document.title=s;
    var b=d[i]("player-iframe"),a=r+window[j].search+window[j].hash;
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




花蝴蝶
http://g.top100.cn/7872775/html/download.html?id=S40dbcfe0c610fa09  这个页面是不变的


http://www.google.cn/music/top100/url?q=http%3A%2F%2Ffile3.top100.cn%2F200904242132%2F84294D05115063D4F5536F601C446632%2FSpecial_123690%2F%25E8%258A%25B1%25E8%259D%25B4%25E8%259D%25B6.mp3&ct=rdl&cad=dl&ei=d7_xSfjsIqPQswKe2s66AQ&sig=D4530353B78C33CA0DDF11C4BA0975ED

http://file3.top100.cn/200904242126/CACD2A931A245597CE61B53A88707497/Special_123690/%E8%8A%B1%E8%9D%B4%E8%9D%B6.mp3


http://www.google.cn/music/top100/url?q=http%3A%2F%2Ffile3.top100.cn%2F200904242258%2FA06A735F67FAD95C3CC3317100A6C00D%2FSpecial_123690%2F%25E8%258A%25B1%25E8%259D%25B4%25E8%259D%25B6.mp3&ct=rdl&cad=dl&ei=p9PxSfiHGp70sAKBktW6AQ&sig=39FE22C230A94C47497AD6A6FCC9DDB4


http://file3.top100.cn/200904242258/A06A735F67FAD95C3CC3317100A6C00D/Special_123690/%E8%8A%B1%E8%9D%B4%E8%9D%B6.mp3



解析
http://www.google.cn/music/top100/url?
q=http%3A%2F
    3A 2F   ?
%2Ffile3.top100.cn
    2F
%2F200904242132   
    当前服务器时间2009年4月24日21:32，比我电脑的慢一分钟。。。
%2F84294D05115063D4F5536F601C446632
    变化
%2FSpecial_123690
    因歌而异
%2F%25E8%258A%25B1%25E8%259D%25B4%25E8%259D%25B6.mp3&   
    25      UTF-8编码？
    E8 8A B1   花
    E8 9D B4   蝴
    E8 9D B6   蝶
ct=rdl&
    category?
cad=dl&
    ?
ei=d7_xSfjsIqPQswKe2s66AQ&
    ?
sig=D4530353B78C33CA0DDF11C4BA0975ED
    sign 私钥？


http://file3.top100.cn/
200904242126/               
    这个和上面的应该完全一样的，这个是解析晚的缘故，太晚就报下面的错:
    403 Forbidden
    CHINACACHE/CCN-BJ-3-57H
CACD2A931A245597CE61B53A88707497/
    ?
Special_123690/
    对应上面
%E8%8A%B1%E8%9D%B4%E8%9D%B6.mp3
    花蝴蝶.mp3














不要在寂寞时说爱我
http://g.top100.cn/7872775/html/download.html?id=Saf76d6e6a33acb96

http://www.google.cn/music/top100/url?q=http%3A%2F%2Ffile3.top100.cn%2F200904242131%2FE8CB1549C16554E438F541DC255915FE%2FSpecial_120448%2F%25E4%25B8%258D%25E8%25A6%2581%25E5%259C%25A8%25E6%2588%2591%25E5%25AF%2582%25E5%25AF%259E%25E7%259A%2584%25E6%2597%25B6%25E5%2580%2599%25E8%25AF%25B4%25E7%2588%25B1%25E6%2588%2591.mp3&ct=rdl&cad=dl&ei=T7_xScjYLqfgsgK2tOC6AQ&sig=2D5A32F85C321FD341E6A1D279E67B48

http://file3.top100.cn/200904242134/4315973706390C6A924761CBD64CDBA2/Special_120448/%E4%B8%8D%E8%A6%81%E5%9C%A8%E6%88%91%E5%AF%82%E5%AF%9E%E7%9A%84%E6%97%B6%E5%80%99%E8%AF%B4%E7%88%B1%E6%88%91.mp3








laputa@laputa-laptop:~/gmbox$ wget http://www.google.cn/music/top100/url?q=http%3A%2F%2Ffile3.top100.cn%2F200904242142%2F139F730279283EAF3AAD3511BEB7B226%2FSpecial_123690%2F%25E8%258A%25B1%25E8%259D%25B4%25E8%259D%25B6.mp3&ct=rdl&cad=dl&ei=xsHxScCdC4iisQKv0eu6AQ&sig=3F1894692C0124FD2E7CBCAAE038E53C
--2009-04-24 21:42:47--  http://www.google.cn/music/top100/url?q=http%3A%2F%2Ffile3.top100.cn%2F200904242142%2F139F730279283EAF3AAD3511BEB7B226%2FSpecial_123690%2F%25E8%258A%25B1%25E8%259D%25B4%25E8%259D%25B6.mp3
Resolving www.google.cn... 203.208.39.104, 203.208.39.99
Connecting to www.google.cn|203.208.39.104|:80... [1] 26481
[2] 26482
[3] 26483
[4] 26484
[2]   Done                    ct=rdl
[3]   Done                    cad=dl
[4]+  Done                    ei=xsHxScCdC4iisQKv0eu6AQ
laputa@laputa-laptop:~/gmbox$ connected.
HTTP request sent, awaiting response... 400 Bad Request
2009-04-24 21:42:47 ERROR 400: Bad Request.


