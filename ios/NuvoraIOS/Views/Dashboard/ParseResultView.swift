import SwiftUI

struct ParseResultView: View {
    let result: ParseTextResponse

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            if let whisper = result.whisperResult {
                Text("語音文字：\(whisper)")
            }
            Text("心率：\(result.gptResult.heartRate.map(String.init) ?? "未提供")")
            Text("喝水量：\(result.gptResult.waterIntake.map(String.init) ?? "未提供")")
            Text("睡眠：\(result.gptResult.sleepHours.map { String(format: "%.1f", $0) } ?? "未提供")")
            Text(result.saved ? "已同步存檔" : "未存檔")
                .font(.footnote.weight(.semibold))
                .foregroundStyle(result.saved ? .green : .orange)
        }
        .font(.footnote)
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color(.secondarySystemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 16))
    }
}
