import Foundation

@MainActor
final class AuthViewModel: ObservableObject {
    @Published var currentUser: User?
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let apiClient: APIClient

    init(apiClient: APIClient) {
        self.apiClient = apiClient
    }

    var isAuthenticated: Bool { currentUser != nil }

    func restoreSession() async {
        guard apiClient.token != nil else { return }
        do {
            let response = try await apiClient.me()
            currentUser = response.user
        } catch {
            apiClient.clearToken()
            currentUser = nil
        }
    }

    func register(username: String, password: String) async {
        await runAuthFlow {
            let response = try await apiClient.register(username: username, password: password)
            currentUser = response.user
        }
    }

    func login(username: String, password: String) async {
        await runAuthFlow {
            let response = try await apiClient.login(username: username, password: password)
            currentUser = response.user
        }
    }

    func logout() async {
        isLoading = true
        defer { isLoading = false }

        do {
            try await apiClient.logout()
        } catch {
            apiClient.clearToken()
        }

        currentUser = nil
    }

    private func runAuthFlow(_ action: () async throws -> Void) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        do {
            try await action()
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? error.localizedDescription
        }
    }
}
