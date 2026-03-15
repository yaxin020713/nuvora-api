import SwiftUI

struct AuthContainerView: View {
    @ObservedObject var authViewModel: AuthViewModel
    @State private var selectedTab = 0

    var body: some View {
        TabView(selection: $selectedTab) {
            LoginView(authViewModel: authViewModel)
                .tabItem { Label("登入", systemImage: "person.fill") }
                .tag(0)

            RegisterView(authViewModel: authViewModel)
                .tabItem { Label("註冊", systemImage: "person.badge.plus") }
                .tag(1)
        }
        .overlay(alignment: .top) {
            if let message = authViewModel.errorMessage {
                Text(message)
                    .padding(10)
                    .background(.ultraThinMaterial)
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                    .padding(.top, 12)
            }
        }
    }
}
