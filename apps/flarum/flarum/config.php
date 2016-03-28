<?php return array (
  'debug' => false,
  'database' => 
  array (
    'driver' => 'mysql',
    'host' => 'db',
    'database' => 'flarum',
    'username' => 'flarum',
    'password' => 'flarum',
    'charset' => 'utf8mb4',
    'collation' => 'utf8mb4_unicode_ci',
    'prefix' => '',
    'strict' => false,
  ),
  'url' => 'http://' . getenv('VIRTUAL_HOST'),
  'paths' => 
  array (
    'api' => 'api',
    'admin' => 'admin',
  ),
);
