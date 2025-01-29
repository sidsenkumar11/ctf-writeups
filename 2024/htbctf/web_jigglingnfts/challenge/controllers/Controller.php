<?php
class Controller 
{
    // The secret is different on remote instance! Please do not try to bruteforce this key
    // Other bruteforce are allowed but don't try to guess this key
    protected $sess_crypt_key = 'efgmhtndr4x8631uvw07oclq';

    public function __construct()
    {
        $this->checkUserCookie();
    }

    protected function getCookie($name)
    {
        return isset($_COOKIE[$name]) ? $_COOKIE[$name] : null;
    }

    protected function setCookie($name, $value, $expire)
    {
        setcookie($name, $value, $expire, "/");
    }

    protected function getUsername()
    {
        if ($cookie = $this->getCookie('session'))
        {    
            
            if (strlen($cookie) > 32)
            { 
                $signature = substr($cookie, -32); // last 32 chars
                $payload = substr($cookie, 0, -32); // everything but the last 32 chars

                if (md5($payload . $this->sess_crypt_key) == $signature)
                {
                    return $payload;
                }
            } 
        }
        return null;
    }

    protected function checkUserCookie()
    {
        if (!$this->getCookie('session'))
        {
            $guestUsername = 'guest_' . uniqid();
            $cookieValue = $guestUsername . md5($guestUsername . $this->sess_crypt_key);
            $this->setCookie('session', $cookieValue, time() + (86400 * 30));
        }
    }
}
?>
