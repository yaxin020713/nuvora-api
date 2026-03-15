import Foundation

@MainActor
final class HealthViewModel: ObservableObject {
    @Published var records: [HealthRecord] = []
    @Published var latestParseResult: ParseTextResponse?
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let apiClient: APIClient

    init(apiClient: APIClient) {
        self.apiClient = apiClient
    }

    func loadHistory() async {
        await perform {
            self.records = try await apiClient.fetchHealthData()
        }
    }

    func submitText(_ text: String, save: Bool) async {
        await perform {
            let response = try await apiClient.parseText(text, save: save)
            self.latestParseResult = response
            if save {
                self.records = try await apiClient.fetchHealthData()
            }
        }
    }

    func addManualData(heartRate: Int?, waterIntake: Int?, sleepHours: Double?) async {
        await perform {
            _ = try await apiClient.addHealthData(
                heartRate: heartRate,
                waterIntake: waterIntake,
                sleepHours: sleepHours
            )
            self.records = try await apiClient.fetchHealthData()
        }
    }

    func uploadAudio(fileURL: URL, save: Bool) async {
        await perform {
            let response = try await apiClient.uploadAudio(fileURL: fileURL, save: save)
            self.latestParseResult = response
            if save {
                self.records = try await apiClient.fetchHealthData()
            }
        }
    }

    private func perform(_ action: () async throws -> Void) async {
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
