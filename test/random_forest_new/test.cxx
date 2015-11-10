/************************************************************************/
/*                                                                      */
/*        Copyright 2014-2015 by Ullrich Koethe and Philip Schill       */
/*                                                                      */
/*    This file is part of the VIGRA computer vision library.           */
/*    The VIGRA Website is                                              */
/*        http://hci.iwr.uni-heidelberg.de/vigra/                       */
/*    Please direct questions, bug reports, and contributions to        */
/*        ullrich.koethe@iwr.uni-heidelberg.de    or                    */
/*        vigra@informatik.uni-hamburg.de                               */
/*                                                                      */
/*    Permission is hereby granted, free of charge, to any person       */
/*    obtaining a copy of this software and associated documentation    */
/*    files (the "Software"), to deal in the Software without           */
/*    restriction, including without limitation the rights to use,      */
/*    copy, modify, merge, publish, distribute, sublicense, and/or      */
/*    sell copies of the Software, and to permit persons to whom the    */
/*    Software is furnished to do so, subject to the following          */
/*    conditions:                                                       */
/*                                                                      */
/*    The above copyright notice and this permission notice shall be    */
/*    included in all copies or substantial portions of the             */
/*    Software.                                                         */
/*                                                                      */
/*    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND    */
/*    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES   */
/*    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND          */
/*    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT       */
/*    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,      */
/*    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING      */
/*    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR     */
/*    OTHER DEALINGS IN THE SOFTWARE.                                   */
/*                                                                      */
/************************************************************************/
#include <vigra/unittest.hxx>
#include <vigra/random_forest_new.hxx>

using namespace vigra;

struct RandomForestTests
{
    void test_base_class()
    {
        typedef BinaryForest Graph;
        typedef Graph::Node Node;
        typedef LessEqualSplitTest<double> SplitTest;
        typedef ArgMaxAcc Acc;
        typedef RandomForest<MultiArray<2, double>, MultiArray<1, int>, SplitTest, Acc> RF;

        // Build a forest from scratch.
        Graph gr;
        PropertyMap<Node, SplitTest> split_tests;
        PropertyMap<Node, size_t> leaf_responses;
        {
            Node n0 = gr.addNode();
            Node n1 = gr.addNode();
            Node n2 = gr.addNode();
            Node n3 = gr.addNode();
            Node n4 = gr.addNode();
            Node n5 = gr.addNode();
            Node n6 = gr.addNode();
            gr.addArc(n0, n1);
            gr.addArc(n0, n2);
            gr.addArc(n1, n3);
            gr.addArc(n1, n4);
            gr.addArc(n2, n5);
            gr.addArc(n2, n6);

            split_tests.insert(n0, SplitTest(0, 0.6));
            split_tests.insert(n1, SplitTest(1, 0.25));
            split_tests.insert(n2, SplitTest(1, 0.75));
            leaf_responses.insert(n3, 0);
            leaf_responses.insert(n3, 0);
            leaf_responses.insert(n4, 1);
            leaf_responses.insert(n5, 2);
            leaf_responses.insert(n6, 3);
        }
        std::vector<int> distinct_labels;
        distinct_labels.push_back(0);
        distinct_labels.push_back(1);
        distinct_labels.push_back(-7);
        distinct_labels.push_back(3);
        auto const pspec = ProblemSpecNew<int>().num_features(2).distinct_classes(distinct_labels);
        RF rf = RF(gr, split_tests, leaf_responses, pspec);

        // Check if the given points are predicted correctly.
        double test_x_values[] = {
            0.2, 0.4, 0.2, 0.4, 0.7, 0.8, 0.7, 0.8,
            0.2, 0.2, 0.7, 0.7, 0.2, 0.2, 0.8, 0.8
        };
        MultiArray<2, double> test_x(Shape2(8, 2), test_x_values);
        int test_y_values[] = {
            0, 0, 1, 1, -7, -7, 3, 3
        };
        MultiArray<1, int> test_y(Shape1(8), test_y_values);
        MultiArray<1, int> pred_y(Shape1(8));
        rf.predict(test_x, pred_y, 1);
        shouldEqualSequence(pred_y.begin(), pred_y.end(), test_y.begin());
    }

    void test_default_rf()
    {
        typedef MultiArray<2, double> Features;
        typedef MultiArray<1, int> Labels;

        double train_x_values[] = {
            0.2, 0.4, 0.2, 0.4, 0.7, 0.8, 0.7, 0.8,
            0.2, 0.2, 0.7, 0.7, 0.2, 0.2, 0.8, 0.8
        };
        Features train_x(Shape2(8, 2), train_x_values);
        int train_y_values[] = {
            0, 0, 1, 1, -7, -7, 3, 3
        };
        Labels train_y(Shape1(8), train_y_values);
        Features test_x(train_x);
        Labels test_y(train_y);

        std::vector<RandomForestOptionTags> splits;
        splits.push_back(RF_GINI);
        splits.push_back(RF_ENTROPY);
        splits.push_back(RF_KSD);
        for (auto split : splits)
        {
            RandomForestNewOptions const options = RandomForestNewOptions()
                                                       .tree_count(1)
                                                       .bootstrap_sampling(false)
                                                       .split(split)
                                                       .n_threads(1);
            auto rf = random_forest(train_x, train_y, options);
            Labels pred_y(test_y.shape());
            rf.predict(test_x, pred_y, 1);
            shouldEqualSequence(pred_y.begin(), pred_y.end(), test_y.begin());
        }
    }
};

struct RandomForestTestSuite : public test_suite
{
    RandomForestTestSuite()
        :
        test_suite("RandomForest test")
    {
        add(testCase(&RandomForestTests::test_base_class));
        add(testCase(&RandomForestTests::test_default_rf));
    }
};

int main(int argc, char** argv)
{
    RandomForestTestSuite forest_test;
    int failed = forest_test.run(testsToBeExecuted(argc, argv));
    std::cout << forest_test.report() << std::endl;
    return (failed != 0);
}
