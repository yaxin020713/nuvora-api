import SwiftUI
import AuthenticationServices

struct RegisterView: View {
    @ObservedObject var authViewModel: AuthViewModel
    @State private var email = ""
    @State private var password = ""
    @State private var inviteCode = ""

    var body: some View {
        NavigationStack {
            Form {
                Section("建立帳號") {
                    TextField("Email", text: $email)
                        .keyboardType(.emailAddress)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()

                    SecureField("密碼", text: $password)

                    TextField("封測邀請碼（若需要）", text: $inviteCode)
                        .textInputAutocapitalization(.characters)
                        .autocorrectionDisabled()
                }

                Section {
                    Button("註冊並登入") {
                        Task {
                            await authViewModel.register(
                                email: email,
                                password: password,
                                inviteCode: inviteCode.isEmpty ? nil : inviteCode
                            )
                        }
                    }
                    .disabled(authViewModel.isLoading || email.isEmpty || password.count < 6)
                }

                Section("或使用 Apple 建立帳號") {
                    SignInWithAppleButton(.signUp) { request in
                        request.requestedScopes = [.fullName, .email]
                    } onCompletion: { result in
                        handleAppleSignIn(result)
                    }
                    .signInWithAppleButtonStyle(.black)
                    .frame(height: 48)
                }
            }
            .navigationTitle("註冊")
        }
    }

    private func handleAppleSignIn(_ result: Result<ASAuthorization, Error>) {
        guard case let .success(authorization) = result,
              let credential = authorization.credential as? ASAuthorizationAppleIDCredential,
              let identityTokenData = credential.identityToken,
              let identityToken = String(data: identityTokenData, encoding: .utf8) else {
            authViewModel.errorMessage = "Apple 註冊失敗，請稍後再試。"
            return
        }

        let givenName = credential.fullName?.givenName ?? ""
        let familyName = credential.fullName?.familyName ?? ""
        let nameParts = [familyName, givenName].filter { !$0.isEmpty }
        let usernameHint = nameParts.joined(separator: "").isEmpty ? nil : nameParts.joined(separator: "")

        Task {
            await authViewModel.signInWithApple(
                identityToken: identityToken,
                email: credential.email,
                usernameHint: usernameHint,
                inviteCode: inviteCode.isEmpty ? nil : inviteCode
            )
        }
    }
}
