import AVFoundation
import Foundation

@MainActor
final class VoiceRecorderViewModel: NSObject, ObservableObject {
    @Published var isRecording = false
    @Published var recordedFileURL: URL?
    @Published var errorMessage: String?

    private var recorder: AVAudioRecorder?

    func startRecording() async {
        do {
            let session = AVAudioSession.sharedInstance()
            try session.setCategory(.playAndRecord, mode: .default)
            try session.setActive(true)

            let granted = await requestMicrophonePermission(session: session)

            guard granted else {
                errorMessage = "麥克風權限未開啟"
                return
            }

            let fileURL = FileManager.default.temporaryDirectory
                .appendingPathComponent(UUID().uuidString)
                .appendingPathExtension("m4a")

            let settings: [String: Any] = [
                AVFormatIDKey: Int(kAudioFormatMPEG4AAC),
                AVSampleRateKey: 12_000,
                AVNumberOfChannelsKey: 1,
                AVEncoderAudioQualityKey: AVAudioQuality.high.rawValue
            ]

            recorder = try AVAudioRecorder(url: fileURL, settings: settings)
            recorder?.record()
            recordedFileURL = nil
            isRecording = true
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func stopRecording() {
        recorder?.stop()
        recordedFileURL = recorder?.url
        recorder = nil
        isRecording = false
    }

    private func requestMicrophonePermission(session: AVAudioSession) async -> Bool {
        if #available(iOS 17.0, *) {
            return await withCheckedContinuation { continuation in
                AVAudioApplication.requestRecordPermission { allowed in
                    continuation.resume(returning: allowed)
                }
            }
        }

        return await withCheckedContinuation { continuation in
            session.requestRecordPermission { allowed in
                continuation.resume(returning: allowed)
            }
        }
    }
}
