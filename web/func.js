async function setParam(){
    //讀取偏好設定，設定最大分群數，最適分群數
    var x = await eel.setBest()();
    $("#best").val(parseInt(x));
    var y = await eel.setMax()();
    $("#ncluster").val(parseInt(y));
}

$( document ).ready(function() {
    //網站載入後設定最大分群數，最適分群數
    setParam();
});

async function about(){
    //填入適用說明區塊
    var x = await eel.about()();
    $('#divabout').html(x);
}

async function calAll(){
    //最大分群數按鈕點擊事件
    alert("即將從第1群開始到你設定的最大分群數分別計算績效圖所需資訊。計算時間視分群數而定，在顯示順利完成前請勿關閉或重新整理視窗。最大分群數設定為10時約需2.5分鐘的運算時間，請耐心等候。");
    var temp = $("#ncluster").val();
    var x = await eel.calAll(parseInt(temp))();
    //alert(x);

    if (x==true) {
        alert("順利完成，請選擇最佳分群數並再次計算。");
        var ifo = " success"
        //alert(x);
    }else {
        alert("計算失敗!!!");
        var ifo = " fail"
        //alert(x);
    };

    location.reload();
    setParam();

}

async function calBest(){
    //最適分群數按鈕點擊事件
    alert("即將進行最適分群數計算。計算時間視分群數而定，在顯示完成與否前請勿關閉或重新整理視窗");
    var temp = $("#best").val();
    var x = await eel.calBest(parseInt(temp))();
    //alert(x);
    
    if (x==true) {
        alert("順利完成，請至最佳結果頁籤察看結果。");
        //alert(x);
    }else {
        alert("計算失敗!!!");
        //alert(x);
    };

    location.reload();
    setParam();
}

async function gotoBest(){
    //參數設定頁最佳結果點擊事件
    $('#gotoBest').click();
};

async function sta(){
    //填入統計資訊
    var x = await eel.sta()();
    
    var xj = JSON.parse(x);
    var xjR = xj.recent;
    var xjF = xj.freq;
    var xjM = xj.money;
    var xjFD = xj.first_days;
    
    for(var i=0; i<xjR.length;i++){
        xjR[i] = Math.round( xjR[i]*1000 )/1000;
        xjF[i] = Math.round( xjF[i]*1000 )/1000;
        xjM[i] = Math.round( xjM[i]*1000 )/1000;
        xjFD[i] = Math.round( xjFD[i]*1000 )/1000;
    };

    $('#countR').html(xjR[0]);
    $('#countF').html(xjF[0]);
    $('#countM').html(xjM[0]);
    $('#countM').html(xjFD[0]);

    $('#meanR').html(xjR[1]);
    $('#meanF').html(xjF[1]);
    $('#meanM').html(xjM[1]);
    $('#meanM').html(xjFD[1]);

    $('#stdR').html(xjR[2]);
    $('#stdF').html(xjF[2]);
    $('#stdM').html(xjM[2]);
    $('#stdM').html(xjFD[2]);

    $('#minR').html(xjR[3]);
    $('#minF').html(xjF[3]);
    $('#minM').html(xjM[3]);
    $('#minM').html(xjFD[3]);

    $('#q1R').html(xjR[4]);
    $('#q1F').html(xjF[4]);
    $('#q1M').html(xjM[4]);
    $('#q1M').html(xjFD[4]);

    $('#q2R').html(xjR[5]);
    $('#q2F').html(xjF[5]);
    $('#q2M').html(xjM[5]);
    $('#q2M').html(xjFD[5]);

    $('#q3R').html(xjR[6]);
    $('#q3F').html(xjF[6]);
    $('#q3M').html(xjM[6]);
    $('#q3M').html(xjFD[6]);

    $('#maxR').html(xjR[7]);
    $('#maxF').html(xjF[7]);
    $('#maxM').html(xjM[7]);
    $('#maxM').html(xjFD[7]);
}