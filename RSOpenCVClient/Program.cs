using System.Runtime.InteropServices;
using RSOpenCVClient;
using SocketIOClient;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Imaging;

[DllImport("user32.dll", SetLastError = true)]
static extern bool GetWindowRect(IntPtr hwnd, out RECT lpRect);

var processes = Process.GetProcesses();
var runeLiteProcess = processes.FirstOrDefault((process) => process.ProcessName == "RuneLite");
if (runeLiteProcess == null)
{
    Console.WriteLine("RuneLite not running you silly goose!!");
    Console.ReadLine();
    return;
}

Console.WriteLine("RuneLite process ID: {0}", runeLiteProcess.Id);
var client = new SocketIO("http://localhost:8000/osrs", new SocketIOOptions(){ReconnectionAttempts = 100, ReconnectionDelay = 10});

var botIdTask = new TaskCompletionSource<string>();
var botId = "";

var botTaskAcceptedTask = new TaskCompletionSource<bool>();

client.On("registration", response =>
{
    botIdTask.SetResult(response.GetValue<string>());
});

client.On("1", response => {
    botTaskAcceptedTask.SetResult(response.GetValue<bool>());
});

async Task BotSetup() {
    botId = await botIdTask.Task;
    Console.WriteLine("Bot ID {0} Registered.", botId);
    Console.WriteLine("Select a task:");
    Console.WriteLine("[1] Motherlode Mine");
    string? result = Console.ReadLine();
    if(String.IsNullOrWhiteSpace(result) || result != "1") {
        Console.WriteLine("No valid option selected. Exiting...");
        System.Environment.Exit(0);
    }
    Console.WriteLine("{0} selected, starting bot connection with server.", result);
    await client.EmitAsync("task", "Motherlode Mine");
    var canStart = await botTaskAcceptedTask.Task;
    if(!canStart) {
        throw new Exception("Server rejected access.");
    }
}

client.OnConnected += async (sender, e) =>
{
    Console.WriteLine("Connected to server.");
    await BotSetup();
    while (client.Connected)
    {
        GetWindowRect(runeLiteProcess.MainWindowHandle, out var lpRect);
        Console.WriteLine("Sending next screenshot");
        using (var bitmap = new Bitmap(lpRect.Width, lpRect.Height))
        {
            using (var g = Graphics.FromImage(bitmap))
            {
                g.CopyFromScreen(lpRect.X, lpRect.Y, 0, 0,
                bitmap.Size, CopyPixelOperation.SourceCopy);
            }
            using (var ms = new MemoryStream())
            {
                bitmap.Save(ms, ImageFormat.Jpeg);
                byte[] byteImage = ms.ToArray();
                Console.WriteLine("image size: {0}kb", byteImage.Length / 1000);
                try {
                    await client.EmitAsync("message", byteImage);
                }
                catch(Exception) {
                }
            }
            await Task.Delay(50);

        }
    }
};

await client.ConnectAsync();
await Task.Delay(-1);