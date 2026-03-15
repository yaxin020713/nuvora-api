import SwiftUI

struct LoginView: View {
    @ObservedObject var authViewModel: AuthViewModel
    @State private var username = ""
    @State private var password = ""

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
            }
            .navigationTitle("登入")
        }
    }
}
