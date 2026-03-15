import Foundation

struct User: Codable, Identifiable, Equatable {
    let id: Int
    let username: String
}

struct AuthResponse: Codable {
    let message: String
    let user: User
    let token: String?
    let tokenType: String?

    enum CodingKeys: String, CodingKey {
        case message
        case user
        case token
        case tokenType = "token_type"
    }
}

struct AuthMeResponse: Codable {
    let authenticated: Bool
    let user: User?
}

struct MessageResponse: Codable {
    let message: String
}

struct HealthRecord: Codable, Identifiable {
    let id: Int
    let userID: String
    let heartRate: Int?
    let waterIntake: Int?
    let sleepHours: Double?

    enum CodingKeys: String, CodingKey {
        case id
        case userID = "user_id"
        case heartRate = "heart_rate"
        case waterIntake = "water_intake"
        case sleepHours = "sleep_hours"
    }
}

struct HealthListResponse: Codable {
    let count: Int
    let items: [HealthRecord]
}

struct AddHealthResponse: Codable {
    let message: String
    let data: HealthRecord
}

struct GPTHealthResult: Codable {
    let heartRate: Int?
    let waterIntake: Int?
    let sleepHours: Double?
}

struct ParseTextResponse: Codable {
    let inputText: String
    let whisperResult: String?
    let gptResult: GPTHealthResult
    let saved: Bool
    let savedRecord: HealthRecord?

    enum CodingKeys: String, CodingKey {
        case saved
        case inputText = "input_text"
        case whisperResult = "whisper_result"
        case gptResult = "gpt_result"
        case savedRecord = "saved_record"
    }
}

struct APIErrorResponse: Codable, Error, LocalizedError {
    let error: String

    var errorDescription: String? { error }
}
