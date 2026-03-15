import SwiftUI

struct TextEntryCard: View {
    @ObservedObject var healthViewModel: HealthViewModel
    @State private var text = ""
    @State private var shouldSave = true

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("文字輸入")
                .font(.headline)

            TextEditor(text: $text)
                .frame(minHeight: 120)
                .padding(8)
                .background(Color(.secondarySystemBackground))
                .clipShape(RoundedRectangle(cornerRadius: 16))

            Toggle("解析後直接存檔", isOn: $shouldSave)

            Button("送出文字") {
                Task {
                    await healthViewModel.submitText(text, save: shouldSave)
                    text = ""
                }
            }
            .buttonStyle(.borderedProminent)
            .disabled(text.isEmpty || healthViewModel.isLoading)

            if let result = healthViewModel.latestParseResult {
                ParseResultView(result: result)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(.thinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 20))
    }
}
