Attribute VB_Name = "Módulo1"
Function TRIANGULAR(R_ALEATORIO, A_PESIMISTA, B_PROBABLE, C_OPTIMISTA)

R = R_ALEATORIO

A = A_PESIMISTA

B = B_PROBABLE

C = C_OPTIMISTA

A1 = (B - A) / (C - A)

If R < A1 Then

    X = A + Sqr(R * (C - A) * (B - A))

Else

    

    X = C - Sqr((1 - R) * (C - A) * (C - B))

 

End If

    TRIANGULAR = X

End Function

