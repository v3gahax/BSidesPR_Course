$serverAddress = "127.0.0.1"  # Change this to your server's IP address or hostname
$serverPort = 2575  # Change this to your server's port number
$message = @"
MSH|^~\&|SendingApp|SendingFac|ReceivingApp|ReceivingFac|20220408120000||ADT^A04|123456|P|2.5|
PID|1||123456||Doe^John^||19600101|M|
"@

while ($true) {
    $client = New-Object System.Net.Sockets.TcpClient
    $client.Connect($serverAddress, $serverPort)
    $stream = $client.GetStream()
    $writer = New-Object System.IO.StreamWriter($stream)
    $reader = New-Object System.IO.StreamReader($stream)

    $writer.WriteLine($message)
    $writer.Flush()

    $response = $reader.ReadLine()
    Write-Host "Response from server: $response"

    $stream.Close()
    $client.Close()

    Start-Sleep -Seconds 5
}
