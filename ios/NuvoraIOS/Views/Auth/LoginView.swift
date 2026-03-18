import SwiftUI
import AuthenticationServices

struct LoginView: View {
    @ObservedObject var authViewModel: AuthViewModel
    @State private var username = ""
    @State private var password = ""
    @State private var inviteCode = ""

    var body: some View {
        NavigationStack {
            Form {
                Section("登入 Nuvora") {
                    TextField("帳號", text: $username)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()

                    SecureField("密碼", text: $password)
                }

                Section {
                    Button("登入") {
                        Task {
                            await authViewModel.login(username: username, password: password)
                        }
                    }
                    .disabled(authViewModel.isLoading || username.isEmpty || password.isEmpty)
                }

                Section("或使用 Apple") {
                    TextField("封測邀請碼（若需要）", text: $inviteCode)
                        .textInputAutocapitalization(.characters)
                        .autocorrectionDisabled()

                    SignInWithAppleButton(.signIn) { request in
                        request.requestedScopes = [.fullName, .email]
                    } onCompletion: { result in
                        handleAppleSignIn(result)
                    }
                    .signInWithAppleButtonStyle(.black)
                    .frame(height: 48)
                }
            }
            .navigationTitle("登入")
        }
    }

    private func handleAppleSignIn(_ result: Result<ASAuthorization, Error>) {
        guard case let .success(authorization) = result,
              let credential = authorization.credential as? ASAuthorizationAppleIDCredential,
              let identityTokenData = credential.identityToken,
              let identityToken = String(data: identityTokenData, encoding: .utf8) else {
            authViewModel.errorMessage = "Apple 登入失敗，請稍後再試。"
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
