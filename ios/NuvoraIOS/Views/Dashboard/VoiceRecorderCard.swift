import SwiftUI

struct VoiceRecorderCard: View {
    @ObservedObject var healthViewModel: HealthViewModel
    @ObservedObject var voiceRecorderViewModel: VoiceRecorderViewModel
    @State private var shouldSave = true

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("語音輸入")
                .font(.headline)

            HStack(spacing: 12) {
                Button(voiceRecorderViewModel.isRecording ? "錄音中..." : "開始錄音") {
                    Task { await voiceRecorderViewModel.startRecording() }
                }
                .buttonStyle(.borderedProminent)
                .disabled(voiceRecorderViewModel.isRecording)

                Button("停止") {
                    voiceRecorderViewModel.stopRecording()
                }
                .buttonStyle(.bordered)
                .disabled(!voiceRecorderViewModel.isRecording)
            }

            if let fileURL = voiceRecorderViewModel.recordedFileURL {
                Text(fileURL.lastPathComponent)
                    .font(.footnote)
                    .foregroundStyle(.secondary)

                Toggle("解析後直接存檔", isOn: $shouldSave)

                Button("上傳錄音") {
                    Task { await healthViewModel.uploadAudio(fileURL: fileURL, save: shouldSave) }
                }
                .buttonStyle(.borderedProminent)
                .disabled(healthViewModel.isLoading)
            } else {
                Text("錄完音後會顯示可上傳的音檔。")
                    .foregroundStyle(.secondary)
            }

            if let result = healthViewModel.latestParseResult, result.whisperResult != nil {
                ParseResultView(result: result)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(.thinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 20))
    }
}
