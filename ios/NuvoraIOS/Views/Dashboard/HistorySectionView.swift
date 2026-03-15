import SwiftUI

struct HistorySectionView: View {
    let records: [HealthRecord]

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("歷史資料")
                .font(.headline)

            if records.isEmpty {
                Text("目前還沒有健康資料。")
                    .foregroundStyle(.secondary)
            } else {
                ForEach(records) { record in
                    VStack(alignment: .leading, spacing: 6) {
                        Text(record.userID)
                            .font(.subheadline.bold())
                        Text("心率：\(record.heartRate.map(String.init) ?? "未提供")")
                        Text("喝水量：\(record.waterIntake.map(String.init) ?? "未提供")")
                        Text("睡眠：\(record.sleepHours.map { String(format: "%.1f", $0) } ?? "未提供")")
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding()
                    .background(Color(.secondarySystemBackground))
                    .clipShape(RoundedRectangle(cornerRadius: 16))
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(.thinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 20))
    }
}
