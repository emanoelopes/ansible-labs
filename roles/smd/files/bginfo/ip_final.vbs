' Dois últimos octetos do IP da placa com gateway (as virtuais não têm).
' Lido pelo campo IP_FINAL do usuario_ip.bgi; Echo é do BGInfo.
Set w = GetObject("winmgmts:")
For Each n In w.ExecQuery("select IPAddress, DefaultIPGateway from Win32_NetworkAdapterConfiguration where IPEnabled=true")
  If Not IsNull(n.DefaultIPGateway) Then
    p = Split(n.IPAddress(0), ".")
    Echo p(2) & "." & p(3)
    Exit For
  End If
Next
