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

client.On("response", response =>
{

});

client.OnConnected += async (sender, e) =>
{
    Console.WriteLine("We're connected, start streaming ASAP!");
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