import SwiftUI

struct DashboardView: View {
    @ObservedObject var authViewModel: AuthViewModel
    @ObservedObject var healthViewModel: HealthViewModel
    @ObservedObject var voiceRecorderViewModel: VoiceRecorderViewModel

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) {
                    headerCard
                    TextEntryCard(healthViewModel: healthViewModel)
                    VoiceRecorderCard(
                        healthViewModel: healthViewModel,
                        voiceRecorderViewModel: voiceRecorderViewModel
                    )
                    HistorySectionView(records: healthViewModel.records)
                }
                .padding()
            }
            .navigationTitle("Nuvora")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("登出") {
                        Task { await authViewModel.logout() }
                    }
                }
            }
            .task {
                await healthViewModel.loadHistory()
            }
            .alert("錯誤", isPresented: Binding(
                get: { healthViewModel.errorMessage != nil || voiceRecorderViewModel.errorMessage != nil },
                set: { _ in
                    healthViewModel.errorMessage = nil
                    voiceRecorderViewModel.errorMessage = nil
                }
            )) {
                Button("好") {}
            } message: {
                Text(healthViewModel.errorMessage ?? voiceRecorderViewModel.errorMessage ?? "")
            }
        }
    }

    private var headerCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("你好，\(authViewModel.currentUser?.username ?? "")")
                .font(.title2.bold())
            Text("用文字或錄音快速新增健康資料，下面會同步顯示你的歷史紀錄。")
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(.thinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 20))
    }
}
