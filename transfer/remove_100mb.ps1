# Define the input and output file paths
$inFile = "C:\Path\To\Your\OriginalFile.ext"
$outFile = "C:\Path\To\Your\ModifiedFile.ext"

$inFile = Read-Host -Prompt "OriginalFile: "
$outFile = Read-Host -Prompt "ModifiedFile: "

# Define the number of bytes to skip (100MB)
$bytesToSkip = 100 * 1024 * 1024 # 100 MB in bytes

# Define the buffer size for reading/writing (e.g., 4KB)
$bufferSize = 4096

# Create a byte array for the buffer
$buffer = New-Object byte[] $bufferSize

# Open the input file for reading
$inStream = [System.IO.File]::OpenRead($inFile)

# Seek past the first 100MB
$inStream.Seek($bytesToSkip, [System.IO.SeekOrigin]::Begin)

# Open the output file for writing (CreateNew prevents overwriting existing files)
$outStream = New-Object System.IO.FileStream $outFile, ([System.IO.FileMode]::CreateNew), ([System.IO.FileAccess]::Write), ([System.IO.FileShare]::None)

# Copy the remaining content
while (($bytesRead = $inStream.Read($buffer, 0, $buffer.Length)) -gt 0) {
    $outStream.Write($buffer, 0, $bytesRead)
}

# Close the streams to release file locks
$outStream.Dispose()
$inStream.Dispose()

Write-Host "First 100MB removed. Modified file saved to: $outFile"
