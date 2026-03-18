import Foundation

final class APIClient {
    private let baseURL: URL
    private let tokenStore: TokenStore

    var token: String? {
        didSet {
            if let token {
                try? tokenStore.save(token: token)
            }
        }
    }

    init(baseURL: URL = APIEnvironment.baseURL, tokenStore: TokenStore = KeychainTokenStore()) {
        self.baseURL = baseURL
        self.tokenStore = tokenStore
        self.token = tokenStore.loadToken()
    }

    func clearToken() {
        token = nil
        try? tokenStore.clearToken()
    }

    private func request(path: String, method: String = "GET") -> URLRequest {
        var request = URLRequest(url: baseURL.appendingPathComponent(path))
        request.httpMethod = method
        if let token {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        return request
    }

    private func send<T: Decodable>(_ request: URLRequest, as type: T.Type) async throws -> T {
        let (data, response) = try await URLSession.shared.data(for: request)
        let decoder = JSONDecoder()

        guard let httpResponse = response as? HTTPURLResponse else {
            throw URLError(.badServerResponse)
        }

        if (200 ..< 300).contains(httpResponse.statusCode) {
            return try decoder.decode(T.self, from: data)
        }

        if let apiError = try? decoder.decode(APIErrorResponse.self, from: data) {
            throw apiError
        }

        throw URLError(.badServerResponse)
    }

    func register(username: String, password: String, inviteCode: String? = nil) async throws -> AuthResponse {
        var request = request(path: "auth/register", method: "POST")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(CredentialsRequest(username: username, password: password, inviteCode: inviteCode))

        let response = try await send(request, as: AuthResponse.self)
        token = response.token
        return response
    }

    func login(username: String, password: String) async throws -> AuthResponse {
        var request = request(path: "auth/login", method: "POST")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(CredentialsRequest(username: username, password: password, inviteCode: nil))

        let response = try await send(request, as: AuthResponse.self)
        token = response.token
        return response
    }

    func signInWithApple(identityToken: String, email: String? = nil, usernameHint: String? = nil, inviteCode: String? = nil) async throws -> AuthResponse {
        var request = request(path: "auth/apple", method: "POST")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(AppleSignInRequest(
            identityToken: identityToken,
            email: email,
            usernameHint: usernameHint,
            inviteCode: inviteCode
        ))

        let response = try await send(request, as: AuthResponse.self)
        token = response.token
        return response
    }

    func me() async throws -> AuthMeResponse {
        try await send(request(path: "auth/me"), as: AuthMeResponse.self)
    }

    func logout() async throws {
        var request = request(path: "auth/logout", method: "POST")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = Data("{}".utf8)
        _ = try await send(request, as: MessageResponse.self)
        clearToken()
    }

    func deleteAccount(password: String) async throws {
        var request = request(path: "auth/account", method: "DELETE")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(DeleteAccountRequest(password: password))
        _ = try await send(request, as: MessageResponse.self)
        clearToken()
    }

    func fetchHealthData() async throws -> [HealthRecord] {
        let response = try await send(request(path: "health-data"), as: HealthListResponse.self)
        return response.items
    }

    func addHealthData(heartRate: Int?, waterIntake: Int?, sleepHours: Double?) async throws -> HealthRecord {
        var request = request(path: "health-data", method: "POST")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONSerialization.data(withJSONObject: [
            "heart_rate": heartRate as Any,
            "water_intake": waterIntake as Any,
            "sleep_hours": sleepHours as Any
        ])
        let response = try await send(request, as: AddHealthResponse.self)
        return response.data
    }

    func parseText(_ text: String, save: Bool = true) async throws -> ParseTextResponse {
        var request = request(path: "parse-text", method: "POST")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(ParseTextRequest(text: text, save: save))
        return try await send(request, as: ParseTextResponse.self)
    }

    func uploadAudio(fileURL: URL, save: Bool = true) async throws -> ParseTextResponse {
        let boundary = UUID().uuidString
        var request = request(path: "whisper", method: "POST")
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

        let audioData = try Data(contentsOf: fileURL)
        let fileName = fileURL.lastPathComponent
        let mimeType = fileURL.pathExtension.lowercased() == "wav" ? "audio/wav" : "audio/m4a"

        var body = Data()
        body.append("--\(boundary)\r\n")
        body.append("Content-Disposition: form-data; name=\"save\"\r\n\r\n")
        body.append("\(save)\r\n")

        body.append("--\(boundary)\r\n")
        body.append("Content-Disposition: form-data; name=\"audio\"; filename=\"\(fileName)\"\r\n")
        body.append("Content-Type: \(mimeType)\r\n\r\n")
        body.append(audioData)
        body.append("\r\n--\(boundary)--\r\n")

        request.httpBody = body
        return try await send(request, as: ParseTextResponse.self)
    }
}

private struct CredentialsRequest: Encodable {
    let username: String
    let password: String
    let inviteCode: String?

    enum CodingKeys: String, CodingKey {
        case username
        case password
        case inviteCode = "invite_code"
    }
}

private struct ParseTextRequest: Encodable {
    let text: String
    let save: Bool
}

private struct DeleteAccountRequest: Encodable {
    let password: String
}

private struct AppleSignInRequest: Encodable {
    let identityToken: String
    let email: String?
    let usernameHint: String?
    let inviteCode: String?

    enum CodingKeys: String, CodingKey {
        case identityToken = "identity_token"
        case email
        case usernameHint = "username_hint"
        case inviteCode = "invite_code"
    }
}

private extension Data {
    mutating func append(_ string: String) {
        append(Data(string.utf8))
    }
}
