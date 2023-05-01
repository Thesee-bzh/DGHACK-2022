# Dev / Coffre fort secret

## Challenge
Le coffre-fort secret ne semble pas déchiffrer correctement. Corrigez-le pour obtenir des points. Il y a peut-être d'autres problèmes, qui sait !

## Inputs
- [SecretVault.go](./SecretVault.go)


## Solution
Here's the patch I applied to the code to make it work:

```diff
diff --git a/SecretVault.go b/Sol.go
index 43153f1..18dcbc6 100644
--- a/SecretVault.go
+++ b/Sol.go
@@ -19,14 +19,14 @@ func Encode(b []byte) string {
 
 func Decode(s string) []byte {
 	data, err := base64.StdEncoding.DecodeString(s)
-	if err == nil {
+	if err != nil {
 		panic(err)
 	}
 	return data
 }
 
 // This method encrypts a given text
-func Encrypt(text, MySecret string) (string, error) {
+func Encrypt(text string, MySecret string) (string, error) {
 	block, err := aes.NewCipher([]byte(MySecret))
 	if err != nil {
 		return "", err
@@ -40,7 +40,7 @@ func Encrypt(text, MySecret string) (string, error) {
 }
 
 // This method decrypts a given text
-func Decrypt(text, MySecret string) (string, error) {
+func Decrypt(text string, MySecret string) (string, error) {
 	block, err := aes.NewCipher([]byte(MySecret))
 	if err != nil {
 		return "", err
@@ -48,9 +48,9 @@ func Decrypt(text, MySecret string) (string, error) {
 	// We first decode the base64 input text
 	cipherText := Decode(text)
 	cfb := cipher.NewCFBDecrypter(block, bytes)
-	plainText := make([]byte, len(cipherText))
-	cfb.XORKeyStream(cipherText, plainText)
-	return string(plainText), nil
+	// plainText := make([]byte, len(cipherText))
+	cfb.XORKeyStream(cipherText, cipherText)
+	return string(cipherText), nil
 }
 
 func IsBase64(s string) bool {
@@ -82,11 +82,12 @@ func main() {
 		return
 	}
 	InputString := strings.Join(os.Args[1:], " ")
-	InputString = strings.Replace(InputString, '\n', "", -1)
+	InputString = strings.Replace(InputString, "\n", "", -1)
 
 	// If the input text is suspected to be an encrypted message, we decrypt it and display its content
 	if IsBase64(InputString) {
-		go handleBase64String(InputString)
+		handleBase64String(InputString)
+	} else {
+		handleNormalString(InputString)
 	}
-	handleNormalString(InputString)
 }


## Python code
Complete solution in [Sol.go](./Sol.go)

