<?php
print "Your IP address is ".$_SERVER['REMOTE_ADDR'];
ini_set('max_execution_time', '800');

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);


function writeMsg($command = "", $etc = "", $script = "query.fcgi") {
    $ch = curl_init("https://webl.vivi.com/cgi-bin/" . $script);

    parse_str($etc, $params);
    $params = array_merge($params, array(
        'username' => 'bannerlrd',
        'password' => 'bannerlrd',
        'block_ad' => '1',
        'command' => $command,
    ));

    curl_setopt_array($ch, array(
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_ENCODING => "",
        CURLOPT_MAXREDIRS => 10,
        CURLOPT_TIMEOUT => 30,
        CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
        CURLOPT_CUSTOMREQUEST => "POST",
        CURLOPT_POSTFIELDS => http_build_query($params),
        CURLOPT_HTTPHEADER => array(
            "user-agent: Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0.2) Gecko/20100101 Firefox/6.0.2",
            "cache-control: no-cache",
            "content-type: application/x-www-form-urlencoded"
        ),
    ));

    $result = curl_exec($ch);
    curl_close($ch);

    return $result;
}


if (isset($_REQUEST["thread_id"]))
    echo str_replace("https://webl.vivi.com/cgi-bin/", "?", writeMsg("", "", "Forum.fpl?operation=thread&topic_id=2&thread_id={$_REQUEST["thread_id"]}&username=bannerlrd&password=bannerlrd"));
else
    echo str_replace("https://webl.vivi.com/cgi-bin/", "?", writeMsg("", "", "Forum.fpl?operation=topic&topic_id=" . (isset($_REQUEST["topic_id"]) ? $_REQUEST["topic_id"] : "2") . "&username=bannerlrd&password=bannerlrd"));

?>
