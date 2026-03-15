import SwiftUI

struct RegisterView: View {
    @ObservedObject var authViewModel: AuthViewModel
    @State private var username = ""
    @State private var password = ""

    var body: some View {
        NavigationStack {
            Form {
                Section("建立帳號") {
                    TextField("帳號", text: $username)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()

                    SecureField("密碼", text: $password)
                }

                Section {
                    Button("註冊並登入") {
                        Task {
                            await authViewModel.register(username: username, password: password)
                        }
                    }
                    .disabled(authViewModel.isLoading || username.count < 3 || password.count < 6)
                }
            }
            .navigationTitle("註冊")
        }
    }
}
