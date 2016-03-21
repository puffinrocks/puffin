<?php

add_action( 'phpmailer_init', 'puffin_phpmailer_init' );
function puffin_phpmailer_init( PHPMailer $phpmailer ) {
    $phpmailer->Host = 'mail';
    $phpmailer->Port = 25;
    $phpmailer->SMTPAuth = false;
    $phpmailer->SMTPSecure = '';
    $phpmailer->SMTPAutoTLS = false;
    $phpmailer->IsSMTP();
}

?>
