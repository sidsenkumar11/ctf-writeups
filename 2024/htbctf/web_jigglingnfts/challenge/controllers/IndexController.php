<?php

class IndexController extends Controller
{
    public function __construct()
    {
        parent::__construct();
    }

    public function index($router)
    {
        $username = $this->getUsername();

        if ($username !== null and strpos($username, 'guest') !== 0) {
            $flag = file_get_contents('/flag.txt');
            $router->view('index', ['flag' => $flag]);
        } else {
            $router->view('index');
        }
    }

}