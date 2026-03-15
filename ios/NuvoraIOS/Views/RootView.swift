import SwiftUI

struct RootView: View {
    @StateObject private var authViewModel: AuthViewModel
    @StateObject private var healthViewModel: HealthViewModel
    @StateObject private var voiceRecorderViewModel = VoiceRecorderViewModel()

    init() {
        let apiClient = APIClient()
        _authViewModel = StateObject(wrappedValue: AuthViewModel(apiClient: apiClient))
        _healthViewModel = StateObject(wrappedValue: HealthViewModel(apiClient: apiClient))
    }

    var body: some View {
        Group {
            if authViewModel.isAuthenticated {
                DashboardView(
                    authViewModel: authViewModel,
                    healthViewModel: healthViewModel,
                    voiceRecorderViewModel: voiceRecorderViewModel
                )
            } else {
                AuthContainerView(authViewModel: authViewModel)
            }
        }
        .task {
            await authViewModel.restoreSession()
            if authViewModel.isAuthenticated {
                await healthViewModel.loadHistory()
            }
        }
    }
}
