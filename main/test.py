

SUBROUTINE Update_Password(email, new_info, type)
    IF Manager THEN
        IF type = "password" THEN
            If (PasswordKey is downloaded) THEN
                Encrypt new_info using PasswordKey
                Send new_info to Server
            ELSE 
                Download PasswordKey
                Update_Password(email, new_info, type)
            ENDIF
        ELIF type in ["URL", "Username", "Title", "AdditionalInfo"] THEN
            Send new_info to Server
        ENDIF
    ENDIF