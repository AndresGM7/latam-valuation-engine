Attribute VB_Name = "Módulo2"
Sub SIMULACION()

Sheets("Simulacion").Visible = True
Sheets("FCL").Visible = True
Sheets("FCL").Select
Range("A1").Select


'true la macro Lmostrara los cambios en pantalla'

Application.ScreenUpdating = False

'Vectores con las variables de salidas'

'Vectores con las variables de salidas'
Dim VPN()
Dim TIR_Proy()
Dim TIR_Inv()

N = InputBox("Número de Iteraciones", "N")

ReDim VPN(N)
ReDim TIR_Proy(N)
ReDim TIR_Inv(N)


For i = 1 To N

'Es como presionar el F9 en Excel'
Calculate

VPN(i) = Sheets("FCL").Cells(27, 7)
TIR_Proy(i) = Sheets("FCL").Cells(25, 7)
TIR_Inv(i) = Sheets("FCL").Cells(26, 7)

Next i

Sheets("Simulacion").Select
Range("A1").Select

Range("B:D").ClearContents

Range("B3").Value = "VPN"
Range("C3").Value = "TIR_Proy"
Range("D3").Value = "TIR_Inv"

'El archivo se guarda en otra hoja'

For i = 1 To N

    Cells(i + 3, 2) = VPN(i)
    Cells(i + 3, 3) = TIR_Proy(i)
    Cells(i + 3, 4) = TIR_Inv(i)
    
Next i

Sheets("FCL").Visible = False
Sheets("Simulacion").Visible = False

Sheets("Panel").Select
Range("X26").Select

End Sub
